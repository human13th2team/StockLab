from app.models.holding import Holding
from app.models.user import User
from app.services.kis_api import KisApi
from app import db
from decimal import Decimal

class PortfolioService:
    def __init__(self):
        self.kis_api = KisApi()

    def get_user_portfolio(self, user_id):
        """
        유저의 포트폴리오 현황 및 수익률 계산
        """
        # 1. 유저 정보 조회 (잔고 확인용)
        user = User.query.get(user_id)
        if not user:
            return None

        # 2. 보유 종목 조회
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
            
            # 종목별 수익률
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

        # 3. 전체 수익률 계산
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
