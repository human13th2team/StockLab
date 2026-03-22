import websocket
import json

import os

from dotenv import load_dotenv

from app.services.kis.auth.auth_to_redis import get_approval_key_from_redis

load_dotenv()
APP_KEY = os.getenv('KIS_APP_KEY')
APP_SECRET = os.getenv('KIS_APP_SECRET')
APPROVAL_KEY = get_approval_key_from_redis()

# 삼성전자 예시
STOCK_CODE = "005930"

def on_message(ws, message):
    print("📩 수신 데이터:")
    print(message)

def on_error(ws, error):
    print("❌ 에러:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 연결 종료")

def on_open(ws):
    print("✅ WebSocket 연결 성공")

    # 실시간 체결가 구독 요청
    data = {
        "header": {
            "approval_key": APPROVAL_KEY,
            "custtype": "P",
            "tr_type": "1",  # 1: 등록
            "content-type": "utf-8"
        },
        "body": {
            "input": {
                "tr_id": "H0STCNT0",  # 국내주식 실시간 체결가 (KRX)
                "tr_key": STOCK_CODE
            }
        }
    }

    ws.send(json.dumps(data))


if __name__ == "__main__":
    url = "ws://ops.koreainvestment.com:21000"

    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()