import os
import sys
import time
import json
import requests
import threading
import websocket
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from app.extensions import redis_client
load_dotenv()

from app.api_clients.auth.kis_auth import get_approval_key

load_dotenv()

STOCK_CODE = "035720"  # 카카오

def fetch_fallback_key():
    print("💡 kis_auth.py가 객체를 반환하거나 캐시가 비어있어 직접 발급을 시도합니다.")
    res = requests.post(
        url=os.getenv("KIS_WS_DOMAIN") + "oauth2/Approval",
        headers={"content-type": "application/json; utf-8"},
        json={"grant_type": "client_credentials",
              "appkey": os.getenv('KIS_APP_KEY'),
              "secretkey": os.getenv('KIS_APP_SECRET')
        }
    )
    if res.status_code == 200:
        return res.json().get('approval_key')
    return None

def on_message(ws, msg):
    if msg.startswith('0') or msg.startswith('1'):
        parts = msg.split('|')
        if len(parts) >= 4 and parts[1] == "H0STCNT0":
            data = parts[3].split('^')
            code = data[0]
            price = int(data[2])
            redis_key = f"price:{code}"
            
            # Redis에 최신 가격 저장
            redis_client.lpush(redis_key, price)
            redis_client.ltrim(redis_key, 0, 9)
            
            # Redis에서 방금 저장한 값 조회하여 확인
            latest_price = redis_client.lindex(redis_key, 0)
            if latest_price:
                latest_price = latest_price.decode('utf-8')
                
            print(f"📩 [웹소켓 수신] {code} 실시간 체결가: {price} | ✅ [Redis 검증] 저장된 값: {latest_price}")
    else:
        if "PINGPONG" not in msg:
            print("📩 [메시지 수신]:", msg)

def on_error(ws, error):
    print("❌ [에러 발생]:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 [웹소켓 연결 종료]")

def on_open(ws):
    print("✅ [웹소켓 연결 성공] 호가 구독을 요청합니다.")
    
    print("🔑 승인키 확인 중...")
    try:
        approval_key_val = get_approval_key()
    except Exception as e:
        print(f"⚠️ get_approval_key() 에러: {e}")
        approval_key_val = None
        
    if not approval_key_val:
        approval_key_val = fetch_fallback_key()
        
    if not approval_key_val:
        print("❌ 승인키를 찾을 수 없습니다. 연결을 종료합니다.")
        ws.close()
        return

    data = {
        "header": {
            "approval_key": approval_key_val,
            "custtype": "P",
            "tr_type": "1",  # 1: 등록
            "content-type": "utf-8"
        },
        "body": {
            "input": {
                "tr_id": "H0STCNT0",
                "tr_key": STOCK_CODE
            }
        }
    }
    ws.send(json.dumps(data))

if __name__ == "__main__":
    print("🚀 [ws_test.py] KIS 실시간 체결가 수신 및 Redis 저장 데모 시작")
    
    ws = websocket.WebSocketApp(
        os.getenv("KIS_WS_DOMAIN"),
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    def stop_ws():
        time.sleep(15)
        print("⏱️ 15초가 경과하여 테스트를 자동으로 안전하게 종료합니다.")
        ws.close()
        
    t = threading.Thread(target=stop_ws)
    t.daemon = True
    t.start()
    
    ws.run_forever()