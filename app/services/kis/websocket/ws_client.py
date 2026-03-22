import dataclasses

import websocket
import json

import os
from dotenv import load_dotenv
from pymysql import connect

from app.services.kis.auth.auth_to_redis import get_approval_key_from_redis

import ws_domestic_dto
from app.services.kis.redis_client import init_redis

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
    # stocks = ('005930','000660','005935')
    stocks = ('035720', '020560') # 시가총액이 20위권 밖인 카카오, 아시아나항공으로 테스트
    for stock in stocks:
        body = dataclasses.asdict(ws_domestic_dto.MarketPriceRequestBody(tr_key=stock))
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
        # high  = int(data[STCK_HGPR_IDX]) # 주식 최고가
        # low   = int(data[STCK_LWPR_IDX]) # 주식 최저가
        redis.lpush(f"price:{data[MKSC_SHRN_ISCD_IDX]}", price)
        redis.ltrim(f"price:{data[MKSC_SHRN_ISCD_IDX]}", 0, 9)
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