import os
from dotenv import load_dotenv
from flask import jsonify

from app.services.kis.redis_client import init_redis

load_dotenv()

class KisApi:
    """한국투자증권 API 연동 서비스 클래스"""
    
    def __init__(self):
        self.app_key = os.getenv('KIS_APP_KEY')
        self.app_secret = os.getenv('KIS_APP_SECRET')
        self.base_url = os.getenv('IMMINATION_DOMAIN') # 실전투자 기준
        self.token = None

    def get_current_price(self, ticker_code):
        """실시간 현재가 조회"""
        redis = init_redis()
        current_price = redis.lindex(f"price:{ticker_code}", 0) #redis에 최신값으로 저장
        return current_price.decode('utf-8') if current_price else None

    def search_stocks(self, query):
        """종목 검색 (명칭/코드)"""
        pass

    def daily_stock(self, ticker_code):

        return jsonify({f"{ticker_code}": ""})
