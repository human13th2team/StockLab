import os
import requests
from dotenv import load_dotenv

load_dotenv()

class KisApi:
    """한국투자증권 API 연동 서비스 클래스"""
    
    def __init__(self):
        self.app_key = os.getenv('KIS_APP_KEY')
        self.app_secret = os.getenv('KIS_APP_SECRET')
        self.base_url = "https://openapi.koreainvestment.com:9443"  # 실전투자 기준
        self.token = None

    def get_access_token(self):
        """접근 토큰 발급"""
        # 실제 구현 시 KIS 가이드에 따라 POST 요청 전송
        # 24시간 유효하므로 Redis 캐싱 등을 권장합니다.
        pass

    def get_current_price(self, ticker_code):
        """실시간 현재가 조회 (구조만 구성, 현재는 0 반환)"""
        # 나중에 실시간 조회 테이블이나 실제 API 연결 시 수정 예정
        return 0

    def search_stocks(self, query):
        """종목 검색 (명칭/코드)"""
        pass
