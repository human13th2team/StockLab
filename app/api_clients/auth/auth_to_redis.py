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

def store_approval_key(value, ttl=86400):
    try:
        r.set("approval_key", value=value, ex=ttl)
    except Exception as e:
        print(f"Store approval_key error: {e}")

def store_access_token(value, ttl=86400):
    try:
        r.set("access_token", value=value, ex=ttl)
    except Exception as e:
        print(f"Store access_token error: {e}")

def get_approval_key_from_redis():
    val = r.get("approval_key")
    if val:
        return val.decode('utf-8') if isinstance(val, bytes) else val
    return ""

def get_access_token_from_redis():
    val = r.get("access_token")
    if val:
        return val.decode('utf-8') if isinstance(val, bytes) else val
    return ""

# 만료(False) 조건: 키가 존재하지 않거나, ttl이 600초 이내로 남은 경우
def is_access_token_ttl_valid():
    token_ttl = r.ttl("access_token")
    if token_ttl < 600: # -2, -1 모두 포함됨
        return False
    return True

def is_approval_key_ttl_valid():
    key_ttl = r.ttl("approval_key")
    if key_ttl < 600: # -2, -1 모두 포함됨
        return False
    return True
