"""
KIS(한국투자증권) OAuth2 토큰 2가지 인메모리 저장

이 모듈은 kis_token.py에서 호출한 함수로 토큰값을 저장하고,
Redis를 사용해 토큰 만료 시 재발급을 관리한다

주요 기능:
    - Redis 저장 후 1일마다 갱신
"""
import os
import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'))

def store_approval_key(value):
    try:
        r.set("approval_key", value=value, nx=True, ex=86000)
    except Exception as e:
        print(f"Store approval_key error: {e}")

def store_access_token(value):
    try:
        r.set("access_token", value=value, nx=True, ex=86000)
    except Exception as e:
        print(f"Store access_token error: {e}")

def get_approval_key_from_redis():
    return r.get("approval_key")

def get_access_token_from_redis():
    return r.get("access_token")
