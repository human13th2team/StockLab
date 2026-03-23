import dataclasses

import websocket
import json

import os
from dotenv import load_dotenv

from app.models.stock import Stock
from app.api_clients.auth.auth_to_redis import get_approval_key_from_redis

import ws_domestic_dto
from app.api_clients.redis_client import init_redis
load_dotenv()
redis = init_redis()

#MKSC_SHRN_ISCD: str  #유가증권 단축 종목코드
MKSC_SHRN_ISCD_IDX = 0
# STCK_PRPR: float    #주식 현재가
STCK_PRPR_IDX = 2
# STCK_HGPR: float    #주식 최고가
STCK_HGPR_IDX = 8
# STCK_LWPR: float    #주식 최저가
STCK_LWPR_IDX = 9

conect_key = get_approval_key_from_redis()

def on_open(ws):
    header = dataclasses.asdict(ws_domestic_dto.MarketPriceRequestHeader(approval_key=conect_key))
    # stocks에 저장된 종목 모두 구독
    stocks = [stock.ticker_code for stock in Stock.query.all()]
    for stock in stocks:
        body = ws_domestic_dto.MarketPriceRequestBody(tr_key=stock).wrap_marketprice_request_body()
        request = {
            "header": header,
            "body": body
        }
        ws.send(json.dumps(request))

    print('🙋‍♀️OPENED connection start!!')

def on_close(ws, status_code, close_msg):
    print('🚪CLOSED close_status_code=', status_code, " close_msg=", close_msg)

def on_message(ws, msg):
    if msg.startswith('0'):
        part = msg.split('|')
        tr_id = part[1]
        raw_data = part[3]
        if tr_id != "H0STCNT0":
            return
        data = raw_data.split('^')
        price = int(data[STCK_PRPR_IDX])
        stock_code = data[MKSC_SHRN_ISCD_IDX]
        # 가장 최신값
        last_price = redis.lindex(f"price:{stock_code}", 0)
        # high  = int(data[STCK_HGPR_IDX]) # 주식 최고가
        # low   = int(data[STCK_LWPR_IDX]) # 주식 최저가 > redis에서 최신값으로 유지할 필요가 있으면 주석 해제
        # 최신값이 존재하하는데 지난 가격과 동일한 경우 저장 안하기
        if last_price is not None and int(last_price) == price:
            print(f"{stock_code} Redis not updated (가격 동일: {price})")
        else:
            redis.lpush(f"price:{stock_code}", price)
            redis.ltrim(f"price:{stock_code}", 0, 9)
            # 체결 엔진 알림 발행
            message = {
                "ticker_code": stock_code,
                "current_price": price
            }
            redis.publish("price_updates", json.dumps(message))

    else:
        print("📩 MESSAGE")
        print(msg)

def on_error(ws, error):
    print("💥ERROR error=", error)

if __name__ == "__main__":
    url = os.getenv('IMMITATION_DOMAIN_WS')

    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()