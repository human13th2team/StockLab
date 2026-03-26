from datetime import datetime

from app.api_clients.auth.kis_auth import get_approval_key, get_access_token
from app.api_clients.rest_api.stock_daily_service import stock_daily_service
from app.extensions import scheduler
from app.api_clients.auth import auth_to_redis
from app.models.stock import Stock

@scheduler.task('interval', id='renewal_redis', seconds=80000, next_run_time=datetime.now())
def renewal_redis():
    print("[Schedule] Interval: renewal_redis")
    is_token_valid = auth_to_redis.is_access_token_ttl_valid()
    is_key_valid = auth_to_redis.is_approval_key_ttl_valid()
    if not is_token_valid:
        get_access_token()
        print("[RENEW] access_token")
    if not is_key_valid:
        get_approval_key()
        print("[RENEW] approval_key")

@scheduler.task('cron', id='get_daily_stock_data', hour='15', minute='31')
def get_daily_stock_data():
    print("[Schedule] Cron: get_daily_stock_data")
    #저장 로직 Stock에 저장된 모든 ticker_code 대해 일별 시세 데이터 저장
    with scheduler.app.app_context():
        all_stocks = Stock.query.with_entities(Stock.ticker_code).all()
        for stock in all_stocks:
            # True이면 20260319 ~ 20260323의 값 요청 > 테스트용
            # False이면 당일 값 요청 > 실전
            print(stock_daily_service.get_stock_daily(stock[0], False))
