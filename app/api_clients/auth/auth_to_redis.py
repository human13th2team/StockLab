from app.extensions import redis_client

def store_approval_key(value):
    try:
        redis_client.set("approval_key", value=value, ex=86400)
    except Exception as e:
        print(f"Store approval_key error: {e}")

def store_access_token(value):
    try:
        redis_client.set("access_token", value=value, ex=86400)
    except Exception as e:
        print(f"Store access_token error: {e}")

def get_approval_key_from_redis():
    val = redis_client.get("approval_key")
    return val.decode("utf-8") if val else ""
def get_access_token_from_redis():
    val = redis_client.get("access_token")
    return val.decode("utf-8") if val else ""

# 만료 조건을 검사, 유효한 인증키인지 확인
def is_access_token_ttl_valid():
    is_token_valid = True
    token_ttl = redis_client.ttl("access_token")
    if (token_ttl is None) or (token_ttl < 7200):
        is_token_valid = False
    return is_token_valid

def is_approval_key_ttl_valid():
    is_key_valid = True
    key_ttl = redis_client.ttl("approval_key")
    if (key_ttl is None) or (key_ttl < 7200):
        is_key_valid = False
    return is_key_valid
