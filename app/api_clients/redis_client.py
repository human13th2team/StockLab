"""
Redis 서버와 연결하는 모듈

이 모듈은 .env로부터 redis 연결에 필요한 파라미터를 읽어 연결을 초기화한다

주요 기능:
    - Redis 인스턴스 생성
"""
import os
import redis
from dotenv import load_dotenv

load_dotenv()

def init_redis():
    r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'))
    return r