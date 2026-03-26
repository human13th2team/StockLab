import time
import json
import os
import requests
from dotenv import load_dotenv

# 프로젝트 루트를 경로에 추가 (모듈 임포트 목적)
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.models.stock import Stock
from app.extensions import redis_client as redis
from app.api_clients.auth.kis_auth import get_access_token
from app import create_app

load_dotenv()

def get_current_price(ticker, access_token):
    """KIS API를 호출하여 현재가 정보를 가져와 Redis에 발행합니다."""
    app_key = os.getenv('KIS_APP_KEY')
    app_secret = os.getenv('KIS_APP_SECRET')
    base_url = os.getenv('IMMITATION_DOMAIN', 'https://openapivts.koreainvestment.com:29443')
    
    url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": app_key,
        "appsecret": app_secret,
        "tr_id": "FHKST01010100",
        "custtype": "P"
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": ticker
    }
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            res_json = res.json()
            if res_json.get('rt_cd') == '0':
                output = res_json.get('output', {})
                base_price = int(output.get('stck_prpr', 0))
                exec_time = output.get('stck_cntg_hour', '--:--:--') # 체결 시각
                
                if base_price > 0:
                    price = base_price
                    
                    # Redis 저장 (리스트 형태 유지)
                    redis.lpush(f"price:{ticker}", price)
                    redis.ltrim(f"price:{ticker}", 0, 9)
                    
                    # 실시간 브로드캐스트 발행
                    message = {
                        "ticker_code": ticker,
                        "current_price": price,
                        "exec_time": exec_time # 시간 정보 추가
                    }
                    redis.publish("price_updates", json.dumps(message))
                    print(f"📊 [Polling] {ticker}: {price} (시간: {exec_time}) (Success)")
                    return True
            else:
                print(f"❌ [Polling] {ticker} Error: {res_json.get('msg1')}")
        else:
            print(f"❌ [Polling] API 호출 실패: {res.status_code}")
    except Exception as e:
        print(f"💥 [Polling] 예외 발생: {e}")
    return False

def main():
    print("🚀 실시간 시세 폴링 클라이언트 시작 (웹소켓 대체용)")
    
    # Flask 앱 컨텍스트 초기화 (StockDB 조회용)
    flask_app = create_app('dev')
    
    with flask_app.app_context():
        # 감시할 종목 리스트 (간단하게 삼성전자, SK하이닉스, 네이버 등 기본값 또는 DB에서 가져옴)
        stocks = [s.ticker_code for s in Stock.query.limit(10).all()]
        if not stocks:
            stocks = ['005930', '000660', '035420'] # 기본값: 삼성전자, 하이닉스, 네이버
            
        print(f"💡 감시 종목: {stocks}")

        while True:
            # 매 루프마다 새로운 엑세스 토큰 확인
            access_token = get_access_token()
            if not access_token:
                print("⚠️ Access Token을 가져올 수 없습니다. 10초 후 재시도합니다.")
                time.sleep(10)
                continue
                
            for ticker in stocks:
                get_current_price(ticker, access_token)
                # API 호출 사이의 짧은 간격 (KIS 초당 제한 방지)
                time.sleep(0.5)
            
            # 한 바퀴 다 돌면 잠시 대기
            print("--- Batch Completed. Waiting 1s ---")
            time.sleep(1)

if __name__ == "__main__":
    main()
