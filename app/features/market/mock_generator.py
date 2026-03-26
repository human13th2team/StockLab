import redis
import os
import json
import random
import time
import pymysql
from dotenv import load_dotenv

load_dotenv()

r = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '7274'),
        database=os.getenv('DB_NAME', 'stocklab'),
        cursorclass=pymysql.cursors.DictCursor
    )

def get_stocks_and_prices():
    """DB에서 종목 리스트와 마지막 가격(또는 기본값)을 가져옵니다."""
    stocks = {}
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT ticker_code, name FROM stocks")
            rows = cursor.fetchall()
            for row in rows:
                # Redis에서 마지막 가격 시도
                last_price = r.lindex(f"price:{row['ticker_code']}", 0)
                if last_price:
                    price = int(last_price)
                else:
                    # 기본 가격 설정 (대략적인 값)
                    if row['ticker_code'] == '005930': price = 75000
                    elif row['ticker_code'] == '000660': price = 180000
                    elif row['ticker_code'] == '035420': price = 195000 # NAVER
                    else: price = 50000
                
                stocks[row['ticker_code']] = {
                    "name": row['name'],
                    "price": price
                }
        conn.close()
    except Exception as e:
        print(f"Error fetching stocks: {e}")
        # fallback
        stocks = {"005930": {"name": "삼성전자", "price": 75000}}
    return stocks

def round_price(price):
    if price < 2000: return (price // 1) * 1
    if price < 5000: return (price // 5) * 5
    if price < 20000: return (price // 10) * 10
    if price < 50000: return (price // 50) * 50
    if price < 200000: return (price // 100) * 100
    if price < 500000: return (price // 500) * 500
    return (price // 1000) * 1000

def generate_mock_prices():
    stocks = get_stocks_and_prices()
    print(f"[*] Mock Price Generator started for {len(stocks)} stocks.")
    
    # 만약 NAVER(035420)가 있다면 target 215000 근처로 맞추기 위해 변동폭 상향 조정 가능
    
    while True:
        # NAVER(035420)는 매 초마다 포함시키고, 추가로 2개 더 랜덤하게 선택
        active_tickers = random.sample(list(stocks.keys()), min(2, len(stocks)))
        if "035420" in stocks and "035420" not in active_tickers:
            active_tickers.append("035420")
        
        for ticker in active_tickers:
            old_price = stocks[ticker]["price"]
            # 0.5% ~ -0.5% 변동 (가시성 상향)
            change = random.uniform(-0.005, 0.005)
            
            # 최소 1틱이라도 변하게 강제 (0이면 소폭 상향)
            if abs(change) < 0.0001: change = 0.0005
            
            new_price = round_price(int(old_price * (1 + change)))
            if new_price == old_price:
                new_price += 100 if random.random() > 0.5 else -100
                new_price = round_price(new_price)
            stocks[ticker]["price"] = new_price
            
            message = {
                "ticker_code": ticker,
                "current_price": new_price,
                "exec_time": time.strftime("%H:%M:%S")
            }
            
            r.lpush(f"price:{ticker}", new_price)
            r.ltrim(f"price:{ticker}", 0, 99)
            r.publish("price_updates", json.dumps(message))
            print(f"[Mock] {stocks[ticker]['name']} ({ticker}): {new_price} ({change:+.4%})")
            
        time.sleep(1) # 매 초마다 업데이트

if __name__ == "__main__":
    try:
        generate_mock_prices()
    except KeyboardInterrupt:
        print("Stopping Mock Generator...")
