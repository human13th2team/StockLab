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

## Redis 초기화
def init_redis():
    redis_host = os.getenv('REDIS_HOST')
    redis_port = os.getenv('REDIS_PORT')

    return redis.Redis(host=redis_host, port=redis_port)

