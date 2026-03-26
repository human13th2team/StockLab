from datetime import datetime

from app.api_clients.auth.kis_auth import get_approval_key, get_access_token
from app.api_clients.rest_api.stock_daily_service import stock_daily_service
from app.extensions import scheduler
from app.models.stock import Stock
from app.extensions import redis_client

@scheduler.task('interval', id='renewal_redis', seconds=40000)
def renewal_redis():
    if redis_client.ttl('access_token') < 6000:
        get_access_token()
        print("⏰ RENEW redis access_token by scheculer")
    if redis_client.ttl('approval_key') < 6000:
        get_approval_key()
        print("⏰ RENEW redis approval_key by scheculer")
    print("⏳ Interval Scheduling: renewal_redis")

@scheduler.task('cron', id='get_daily_stock_data', hour='10', minute='08')
def get_daily_stock_data():
    print("⏳ Interval Schedule: get_daily_stock_data")
    #저장 로직 Stock에 저장된 모든 ticker_code 대해 일별 시세 데이터 저장
    with scheduler.app.app_context():
        all_stocks = Stock.query.with_entities(Stock.ticker_code).all()
        for stock in all_stocks:
            # True이면 get_stock_daily에서 수동으로 값 조정 > 메인페이지 테스트용
            # False이면 당일 값 요청 > 실전
            print(stock_daily_service.get_stock_daily(stock[0], False))
