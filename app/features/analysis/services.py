import os
import json
import logging
import datetime
import numpy as np
from decimal import Decimal

# 외부 라이브러리 (기존 환경에 맞게 조정 필요)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 앱 내 모델 및 확장 모듈 (순환 참조가 발생한다면 함수 내 임포트를 유지하되, 가급적 구조 개선 권장)
from app.extensions import db
from app.models.user import User
from app.models.holding import Holding
from app.models import StockDailyData

# --- 로거 전역 설정 (FundingService 용) ---
funding_logger = logging.getLogger("weekly_funding")
if not funding_logger.handlers:
    log_path = os.path.join(os.path.dirname(__file__), "funding.log")
    handler = logging.FileHandler(log_path)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    funding_logger.addHandler(handler)
    funding_logger.setLevel(logging.INFO)


class PortfolioService:
    def get_user_portfolio(self, user_id):
        """유저의 포트폴리오 현황 및 수익률 계산"""
        user = User.query.get(user_id)
        if not user:
            return self._get_empty_portfolio()

        holdings = Holding.query.filter_by(user_id=user_id).all()
        valid_holdings = [h for h in holdings if h.available_qty > 0]
        
        if not valid_holdings:
            return self._build_portfolio_response(user, [], Decimal('0'), Decimal('0'), {"labels": [], "data": []}, {"labels": [], "matrix": []})

        # 1. N+1 문제 해결: 보유 종목들의 최신 주가를 한 번의 쿼리로 매핑
        ticker_codes = [h.ticker_code for h in valid_holdings]
        latest_prices = self._get_latest_prices_bulk(ticker_codes)

        portfolio_items = []
        total_purchase_amount = Decimal('0')
        total_current_value = Decimal('0')

        for holding in valid_holdings:
            # 매핑된 최신 주가 가져오기 (없으면 매입단가)
            current_price = latest_prices.get(holding.ticker_code, holding.avg_price)
            
            purchase_amount = holding.avg_price * holding.available_qty
            current_value = current_price * holding.available_qty
            roi = self._calculate_roi(purchase_amount, current_value)
            
            portfolio_items.append({
                "ticker_code": holding.ticker_code,
                "stock_name": holding.stock.name if holding.stock else holding.ticker_code,
                "qty": holding.available_qty,
                "avg_price": float(holding.avg_price),
                "current_price": float(current_price),
                "purchase_amount": float(purchase_amount),
                "current_value": float(current_value),
                "roi": float(round(roi, 2))
            })
            
            total_purchase_amount += purchase_amount
            total_current_value += current_value

        return_trend = self._get_return_trend(valid_holdings)
        correlation_matrix = self._get_correlation_matrix(valid_holdings)

        return self._build_portfolio_response(user, portfolio_items, total_purchase_amount, total_current_value, return_trend, correlation_matrix)

    def _get_latest_prices_bulk(self, ticker_codes):
        """여러 종목의 최신 종가를 한 번에 조회하여 딕셔너리로 반환"""
        # 가장 최근 날짜 조회 (간단한 구현, DB 구조에 따라 서브쿼리로 최적화 가능)
        latest_date_record = StockDailyData.query.order_by(StockDailyData.stk_date.desc()).first()
        if not latest_date_record:
            return {}
            
        latest_data = StockDailyData.query.filter(
            StockDailyData.ticker_code.in_(ticker_codes),
            StockDailyData.stk_date == latest_date_record.stk_date
        ).all()
        
        return {data.ticker_code: Decimal(str(data.close_price)) for data in latest_data}

    def _calculate_roi(self, purchase, current):
        """수익률 계산 (0 나누기 방지)"""
        if purchase <= 0:
            return Decimal('0')
        return ((current - purchase) / purchase) * 100

    def _build_portfolio_response(self, user, items, total_purchase, total_current, trend, corr_matrix):
        """응답 딕셔너리 생성"""
        total_roi = self._calculate_roi(total_purchase, total_current)
        return {
            "user_nickname": user.nickname,
            "cash": float(user.cash),
            "deposit": float(user.deposit),
            "total_asset": float(user.cash) + float(total_current),
            "total_purchase_amount": float(total_purchase),
            "total_current_value": float(total_current),
            "total_roi": float(round(total_roi, 2)),
            "holdings": items,
            "return_trend": trend,
            "correlation_matrix": corr_matrix
        }

    def _get_empty_portfolio(self):
        return {
            "user_nickname": "알 수 없음", "cash": 0, "deposit": 0, "total_asset": 0,
            "total_purchase_amount": 0, "total_current_value": 0, "total_roi": 0,
            "holdings": [], "error": "사용자를 찾을 수 없습니다."
        }

    def _get_return_trend(self, holdings):
        if not holdings:
            return {"labels": [], "data": []}
            
        dates = db.session.query(StockDailyData.stk_date)\
                          .distinct().order_by(StockDailyData.stk_date.desc()).limit(10).all()
        dates = sorted([d[0] for d in dates])
        
        # N*M 쿼리 개선: 해당 날짜와 보유 종목들에 대한 데이터를 한 번에 가져옴
        ticker_codes = [h.ticker_code for h in holdings]
        price_records = StockDailyData.query.filter(
            StockDailyData.stk_date.in_(dates),
            StockDailyData.ticker_code.in_(ticker_codes)
        ).all()
        
        # (날짜, 티커) -> 가격 매핑
        price_map = {(r.stk_date, r.ticker_code): Decimal(str(r.close_price)) for r in price_records}
        
        trend_values = []
        for date in dates:
            daily_total = Decimal('0')
            for h in holdings:
                price = price_map.get((date, h.ticker_code), h.avg_price)
                daily_total += price * h.available_qty
            trend_values.append(float(daily_total))
            
        return {"labels": [d.strftime("%m-%d") for d in dates], "data": trend_values}

    def _get_correlation_matrix(self, holdings):
        tickers = [h.ticker_code for h in holdings[:5]]
        if len(tickers) < 2:
            return {"labels": tickers, "matrix": [[1.0]]}
            
        all_returns = []
        valid_tickers = []
        
        for ticker in tickers:
            prices = db.session.query(StockDailyData.close_price)\
                               .filter_by(ticker_code=ticker)\
                               .order_by(StockDailyData.stk_date.desc())\
                               .limit(11).all()
            if len(prices) < 2: 
                continue
                
            prices_list = [float(p[0]) for p in reversed(prices)]
            returns = np.diff(prices_list) / prices_list[:-1]
            all_returns.append(returns)
            valid_tickers.append(ticker)
            
        if len(valid_tickers) < 2:
            return {"labels": valid_tickers, "matrix": [[1.0]]}
            
        try:
            corr_mat = np.corrcoef(all_returns)
            matrix = corr_mat.tolist() if isinstance(corr_mat, np.ndarray) else [[float(corr_mat)]]
            return {"labels": valid_tickers, "matrix": matrix}
        except Exception as e:
            logging.error(f"상관관계 행렬 계산 오류: {str(e)}")
            return {"labels": valid_tickers, "matrix": []}


class AnalysisAIService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', "gemini-2.5-flash")
        self.model = ChatGoogleGenerativeAI(
            model=self.model_name, 
            google_api_key=self.api_key, 
            temperature=0.7
        ) if self.api_key else None

        # 프롬프트를 미리 컴파일 (성능 최적화)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 전문 포트폴리오 매니저입니다. 
            사용자의 자산 배분과 수익률을 분석하여 다음 형식을 갖춘 리포트를 500자 이내로 작성하세요.
            1. [투자 성향]: 현재 데이터를 통한 성향 진단 (예: 공격형, 안정추구형 등)
            2. [포트폴리오 평가]: 자산 배분의 장단점 및 강약점 분석
            3. [전략적 추천]: 향후 추천할 종목 2~3개와 구체적인 이유"""),
            ("user", "[사용자 포트폴리오 데이터]\n{portfolio_json}\n\n위 내용을 바탕으로 전문적인 투자 분석 리포트를 작성해 주세요.")
        ])

    def get_trend_analysis(self, portfolio_data):
        if not self.model:
            return "AI API 키가 설정되지 않았습니다. .env 파일을 확인해 주세요."

        chain = self.prompt | self.model | StrOutputParser()

        try:
            portfolio_json = json.dumps(portfolio_data, ensure_ascii=False)
            advice = chain.invoke({"portfolio_json": portfolio_json})
            
            # 단어 잘림 방지를 위해 단순 슬라이싱보다는 여유를 둠
            return advice[:497] + "..." if len(advice) > 500 else advice
        except Exception as e:
            logging.error(f"AI Analysis Error: {str(e)}")
            return "AI 분석 중 일시적인 오류가 발생했습니다."

    def get_investment_advice(self, portfolio_data):
        return self.get_trend_analysis(portfolio_data)


class FundingService:
    @staticmethod
    def pay_user_cash(user_id, amount):
        user = User.query.get(user_id)
        if not user:
            raise ValueError("해당 사용자를 찾을 수 없습니다.")

        user.cash += int(amount)
        db.session.commit()
        return int(user.cash)
    
    @staticmethod
    def run_weekly_funding(manual=False):
        current_week = datetime.datetime.now().strftime("%Y-%W")
        # MariaDB를 사용한 상태 관리 (system@internal 유한 가상 사용자 활용)
        system_user = User.query.filter_by(email="system@internal").first()
        if not system_user:
            # 부재 시 생성 (비밀번호는 사용하지 않으므로 랜덤 또는 고정값)
            system_user = User(
                email="system@internal",
                nickname="SYSTEM_INITIAL",
                password="SYSTEM_LOCKED_ACCOUNT",
                roles=True, # 관리자 권한 부여
                cash=0
            )
            db.session.add(system_user)
            db.session.commit()

        last_funded = system_user.nickname
        if last_funded == current_week:
            if manual:
                funding_logger.info(f"알림: 이번 주({current_week}) 자금은 이미 지급되었습니다.")
            return

        FUNDING_AMOUNT = 10000000
        reason = "정기 스케줄 지급" if not manual else "서버 재가동에 따른 미지급분 소급 지급"
        
        try:
            # 벌크 업데이트: 반복문 없이 DB 레벨에서 단일 쿼리로 전체 업데이트 (가장 중요한 성능 개선점)
            updated_count = User.query.filter_by(roles=False).update(
                {"cash": User.cash + FUNDING_AMOUNT},
                synchronize_session=False # 성능 향상을 위해 세션 동기화 생략
            )
            db.session.commit()
            
            # 상태 업데이트 (MariaDB)
            system_user.nickname = current_week
            db.session.commit()
            
            funding_logger.info(f"✅ {reason} 완료: {updated_count}명에게 지급됨 (주차: {current_week})")
            
        except Exception as e:
            db.session.rollback()
            funding_logger.error(f"❌ {reason} 실패: {str(e)}")