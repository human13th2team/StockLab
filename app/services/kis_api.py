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
        """실시간 현재가 조회 (테스트용 목업)"""
        # 실제 구현 전까지는 테스트를 위해 고정가 또는 랜덤가 반환
        mock_prices = {
            "005930": 72000,  # 삼성전자
            "000660": 160000, # SK하이닉스
            "035420": 180000  # NAVER
        }
        return mock_prices.get(ticker_code, 50000)

    def search_stocks(self, query):
        """종목 검색 (명칭/코드)"""
        pass
