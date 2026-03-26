import threading

import websocket
import json

import os
from dotenv import load_dotenv

from app.api_clients.auth import kis_auth
from app.models.stock import Stock
from app.extensions import redis_client
from app.api_clients.auth.auth_to_redis import get_approval_key_from_redis

from app.api_clients.websocket import ws_domestic_dto
from app.api_clients.redis_client import init_redis
load_dotenv()

#MKSC_SHRN_ISCD: str  #유가증권 단축 종목코드
MKSC_SHRN_ISCD_IDX = 0
# STCK_PRPR: float    #주식 현재가
STCK_PRPR_IDX = 2
# STCK_HGPR: float    #주식 최고가
STCK_HGPR_IDX = 8
# STCK_LWPR: float    #주식 최저가
STCK_LWPR_IDX = 9
# OPRC_VRSS_PRPR_SIGN #시가대비구분(str)
OPRC_VRSS_PRPR_SIGN_IDX = 25
# OPRC_VRSS_PRPR      #시가 대비(num)
OPRC_VRSS_PRPR_IDX = 26

def calculate_oprc_vrss_rate(current_price, sign, vrss):
    """시가, 시가대비 연산으로 등락률 집계"""
    if sign in ['1', '2']:
        opening_price = current_price - vrss
    elif sign in ['4', '5']:
        opening_price = current_price + vrss
    else:
        return "0.00%"

    if opening_price == 0: return "0.00%"
    rate = (vrss / opening_price) * 100

    prefix = "+" if sign in ['1', '2'] else ""
    return f"{prefix}{rate:.2f}%"

def on_open(ws):
    """stocks 테이블에 저장된 종목을 구독하고, 시세 변동을 포착하기 위한 소켓통신"""
    conect_key = get_approval_key_from_redis()
    header = ws_domestic_dto.MarketPriceRequestHeader(approval_key=conect_key).to_dict()
    # stocks 테이블에 저장된 종목 모두 구독
    stocks = [stock.ticker_code for stock in Stock.query.all()]
    for stock in stocks:
        body = ws_domestic_dto.MarketPriceRequestBody(tr_key=stock).wrap_marketprice_request_body()
        request = {
            "header": header,
            "body": body
        }
        ws.send(json.dumps(request))

    print('✅ OPENED connection start!!')

def on_close(ws, status_code, close_msg):
    print('🚪 CLOSED close_status_code=', status_code, " close_msg=", close_msg)

def on_message(ws, msg):
    """실시간 체결가를 받아와서 Redis에 저장"""
    if msg.startswith('0'):
        part = msg.split('|')
        tr_id = part[1]
        raw_data = part[3]
        if tr_id != "H0STCNT0":
            return
        data = raw_data.split('^')
        price = int(data[STCK_PRPR_IDX])
        stock_code = data[MKSC_SHRN_ISCD_IDX]
        # 기존에 저장된 가장 최신값
        last_price = redis_client.lindex(f"price:{stock_code}", 0)
        high  = int(data[STCK_HGPR_IDX]) # 주식 최고가
        low   = int(data[STCK_LWPR_IDX]) # 주식 최저가

        # 기존에 저장된 최신값과 현재 체결가가 동일하면 Redis에 저장하지 않는다
        if last_price is not None and int(last_price) == price:
            print(f"{stock_code} Redis not updated (가격 동일: {price})")
        # 새로운 값이 들어온 경우 Redis에 저장한다
        else:
            redis_client.lpush(f"price:{stock_code}", price)
            redis_client.ltrim(f"price:{stock_code}", 0, 9)
            # 체결 엔진(execution)에 알림 발행
            message = {
                "ticker_code": stock_code,
                "current_price": price
            }
            redis_client.publish("price_updates", json.dumps(message))

            # 홈페이지(home)에 등락률 변동을 알리기 위한 알림 발행
            oprc_vrss_rate = calculate_oprc_vrss_rate(price, data[OPRC_VRSS_PRPR_SIGN_IDX], int(data[OPRC_VRSS_PRPR_IDX]))
            redis_client.set(f"oprc_vrss:{stock_code}", oprc_vrss_rate)
            home_msg = {
                "stock_code": stock_code,
                "oprc_vrss_rate": oprc_vrss_rate,
                "higher_price": high,
                "lowest_proce": low
            }
            redis_client.publish("oprc_vrss_updates", json.dumps(home_msg))
    else:
        pass
        # 메시지가 너무 많아서 주석처리
        # print("📩 MESSAGE" + msg)

def on_error(ws, error):
    print("💥 Socket error=", error)

def run_websocket(app):
    with app.app_context():
        url = os.getenv('KIS_WS_DOMAIN')
        ws = websocket.WebSocketApp(
            url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        ws.run_forever()

def start_websocket_client(app):
    thread = threading.Thread(target=run_websocket, args=(app,), daemon=True)
    thread.start()