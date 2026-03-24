from app.api_clients.auth.kis_auth import get_approval_key, get_access_token
from app.extensions import scheduler
from app.api_clients.auth import auth_to_redis

@scheduler.task('interval', id='renewal_redis', seconds=30000)
def renewal_redis():
    is_token_valid = auth_to_redis.is_access_token_ttl_valid()
    is_key_valid = auth_to_redis.is_approval_key_ttl_valid()

    if not is_token_valid:
        get_access_token()
        print("⏰ RENEW redis access_token by scheculer")
    if not is_key_valid:
        get_approval_key()
        print("⏰ RENEW redis approval_key by scheculer")

@scheduler.task('cron', id='get_daily_stock_data', hour='15', minute='31')
def get_daily_stock_data():
    #저장 로직
    pass

#test 용도로 한번 실행되도록
@scheduler.task('interval', id='test_get_daily_stock_data', seconds=10000)
def get_daily_stock_data():
    #저장 로직
    pass