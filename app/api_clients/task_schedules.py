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

@scheduler.task('cron', id='get_daily_stock_data', hour='15', minute='30')
def get_daily_stock_data():
    #저장 로직
    pass