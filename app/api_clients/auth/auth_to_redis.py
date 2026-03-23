"""
KIS(한국투자증권) OAuth2 토큰 2가지 인메모리 저장

이 모듈은 kis_token.py에서 호출한 함수로 토큰값을 저장한다

주요 기능:
    - Redis 저장 및 조회
"""

from dotenv import load_dotenv

from app.api_clients import redis_client

load_dotenv()

r = redis_client.init_redis()
def redis_connection():
    return r

def store_approval_key(value):
    try:
        # 유효기간은 하루(86,400s)지만, 만료 전 갱신을 위해 86,000으로 TTL 설정
        r.set("approval_key", value=value, ex=86000)
    except Exception as e:
        print(f"Store approval_key error: {e}")

def store_access_token(value):
    try:
        r.set("access_token", value=value, ex=86000)
    except Exception as e:
        print(f"Store access_token error: {e}")

def get_approval_key_from_redis():
    val = r.get("approval_key")
    return val.decode("utf-8") if val else ""
def get_access_token_from_redis():
    val = r.get("access_token")
    return val.decode("utf-8") if val else ""

# 만료(False) 조건: 키가 존재하지 않거나, ttl이 600초 이내로 남은 경우
def is_access_token_ttl_expired():
    is_token_expired = True
    token_ttl = r.ttl("access_token")
    if (token_ttl is None) or (token_ttl < 600):
        is_token_expired = False
    return is_token_expired

def is_approval_key_ttl_expired():
    is_key_expired = True
    key_ttl = r.ttl("approval_key")
    if (key_ttl is None) or (key_ttl < 600):
        is_key_expired = False
    return is_key_expired
