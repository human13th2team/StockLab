"""
KIS(한국투자증권) OAuth2 토큰 2가지 인메모리 저장

이 모듈은 kis_token.py에서 호출한 함수로 토큰값을 저장한다

주요 기능:
    - Redis 저장 및 조회
"""

from dotenv import load_dotenv

from app.services.kis import redis_client

load_dotenv()

r = redis_client.init_redis()
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
    return r.get("approval_key").decode("utf-8")

def get_access_token_from_redis():
    return r.get("access_token").decode("utf-8")
