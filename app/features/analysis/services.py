import os
import json
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv

# LangChain / AI 관련 임포트
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# SQLAlchemy / Model 관련 임포트
from app import db
from app.models.holding import Holding
from app.models.user import User

load_dotenv()

class KisApi:
    """
    Mock KisApi: 외부 증권사 API 연동이 필요할 경우 여기에 구현하거나
    시스템 내의 서비스를 호출함. 현재는 모의 데이터를 제공.
    """
    def get_current_price(self, ticker_code):
        # 주요 종목 모의 가격 (삼성전자, SK하이닉스 등)
        mock_prices = {
            "005930": 78500,
            "000660": 189000,
            "035420": 185000,
            "035720": 48000
        }
        return mock_prices.get(ticker_code, 50000)

class PortfolioService:
    def __init__(self):
        self.kis_api = KisApi()

    def get_user_portfolio(self, user_id):
        """
        유저의 포트폴리오 현황 및 수익률 계산
        """
        user = User.query.get(user_id)
        if not user:
            # 유저가 없을 경우 빈 기본 구조 반환
            return {
                "user_nickname": "알 수 없음",
                "cash": 0,
                "deposit": 0,
                "total_asset": 0,
                "total_purchase_amount": 0,
                "total_current_value": 0,
                "total_roi": 0,
                "holdings": [],
                "error": "사용자를 찾을 수 없습니다."
            }

        holdings = Holding.query.filter_by(user_id=user_id).all()
        
        portfolio_items = []
        total_purchase_amount = Decimal('0')
        total_current_value = Decimal('0')

        for holding in holdings:
            if holding.available_qty <= 0:
                continue

            # 현재가 가져오기
            current_price = Decimal(str(self.kis_api.get_current_price(holding.ticker_code)))
            
            # 매입 금액 및 현재 평가 금액 계산
            purchase_amount = holding.avg_price * holding.available_qty
            current_value = current_price * holding.available_qty
            
            # 종목별 수익률 (제로 나누기 방지)
            roi = ((current_value - purchase_amount) / purchase_amount * 100) if purchase_amount > 0 else Decimal('0')
            
            portfolio_items.append({
                "ticker_code": holding.ticker_code,
                "qty": holding.available_qty,
                "avg_price": float(holding.avg_price),
                "current_price": float(current_price),
                "purchase_amount": float(purchase_amount),
                "current_value": float(current_value),
                "roi": float(round(roi, 2))
            })
            
            total_purchase_amount += purchase_amount
            total_current_value += current_value

        # 전체 수익률 계산 (제로 나누기 방지)
        total_roi = ((total_current_value - total_purchase_amount) / total_purchase_amount * 100) if total_purchase_amount > 0 else Decimal('0')
        
        return {
            "user_nickname": user.nickname,
            "cash": float(user.cash),
            "deposit": float(user.deposit),
            "total_asset": float(user.cash + total_current_value),
            "total_purchase_amount": float(total_purchase_amount),
            "total_current_value": float(total_current_value),
            "total_roi": float(round(total_roi, 2)),
            "holdings": portfolio_items
        }

class AnalysisAIService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            self.model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=self.api_key,
                temperature=0.7
            )
        else:
            self.model = None

    def get_trend_analysis(self, portfolio_data):
        """
        이동평균선 추이 분석 및 유사 종목 추천
        """
        if not self.model:
            return "AI API 키가 설정되지 않았습니다. .env 파일을 확인해 주세요."

        prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 기술적 분석과 차트 패턴 전문가입니다. 사용자의 보유 종목 추세를 분석하여 이동평균선(MA) 흐름이 유사하거나 보완적인 종목을 추천하세요."),
            ("user", """
            현재 나의 보유 종목 및 포트폴리오 상태입니다:
            {portfolio_json}
            
            [분석 및 추천 요청]
            1. 보유 종목들의 최근 이동평균선(5일, 20일, 60일) 추세가 '정배열 상승', '역배열 하락', '횡보' 중 어디에 해당할지 기술적으로 추론하세요.
            2. 이와 유사한 기술적 흐름(거래량 동반 돌파, 정배열 초기 등)을 보이는 종목을 2~3개 추천하세요.
            3. 추천 종목이 왜 현재 포트폴리오와 '이동선 추이' 면에서 유사하거나 전략적 가치가 있는지 전문적으로 설명하세요.
            500자 이내로 명확하고 신뢰감 있는 톤으로 작성하세요.
            """)
        ])

        chain = prompt | self.model | StrOutputParser()

        try:
            portfolio_json = json.dumps(portfolio_data, ensure_ascii=False, indent=2)
            advice = chain.invoke({"portfolio_json": portfolio_json})
            
            if len(advice) > 500:
                advice = advice[:497] + "..."
                
            return advice
        except Exception as e:
            return f"AI 트렌드 분석 중 오류가 발생했습니다: {str(e)}"

    def get_investment_advice(self, portfolio_data):
        """기존 인터페이스 하위 호환"""
        return self.get_trend_analysis(portfolio_data)
