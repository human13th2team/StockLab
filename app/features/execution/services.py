from app.extensions import db
from app.models.order import Order, OrderStatus, OrderType
from app.models.execution import Execution
from app.models.holding import Holding
from datetime import datetime

class ExecutionService:
    """주식 체결 엔진 서비스"""

    @staticmethod
    def check_and_execute_orders(ticker_code, current_price):
        """
        특정 종목의 실시간 가격이 들어왔을 때, 
        해당 종목의 PENDING 주문들을 조회하여 체결 조건이 맞으면 처리합니다.
        """
        # 1. 해당 종목의 PENDING 상태인 주문 조회
        pending_orders = Order.query.filter_by(
            ticker_code=ticker_code, 
            status=OrderStatus.PENDING
        ).all()

        executed_count = 0
        for order in pending_orders:
            # 2. 체결 조건 확인 (지정가 매칭)
            # 매수: 현재가 <= 목표가 이면 체결
            # 매도: 현재가 >= 목표가 이면 체결
            is_match = False
            if order.order_type == OrderType.BUY and current_price <= order.target_price:
                is_match = True
            elif order.order_type == OrderType.SELL and current_price >= order.target_price:
                is_match = True

            if is_match:
                ExecutionService._handle_execution(order, current_price)
                executed_count += 1
        
        if executed_count > 0:
            db.session.commit()
            print(f"[Execution] {ticker_code} 종목 {executed_count}건 체결 완료 (현재가: {current_price})")
        
        return executed_count

    @staticmethod
    def _handle_execution(order, final_price):
        """실제 체결 처리 (트랜잭션 내부)"""
        # 1. 주문 상태 변경
        order.status = OrderStatus.COMPLETED

        # 2. 체결 내역(Execution) 생성
        execution = Execution(
            order_id=order.id,
            user_id=order.user_id,
            final_price=final_price,
            quantity=order.quantity,
            created_at=datetime.utcnow()
        )
        db.session.add(execution)

        # 3. 자산(cash, deposit) 및 홀딩(Holdings) 업데이트
        from app.models.user import User
        user = User.query.get(order.user_id)
        holding = Holding.query.filter_by(user_id=order.user_id, ticker_code=order.ticker_code).first()
        
        total_price = final_price * order.quantity

        if order.order_type == OrderType.BUY:
            # 현금 차감 및 예수금(투자금) 증가
            user.cash -= total_price
            user.deposit += total_price

            if holding:
                # 평균 단가 및 수량 업데이트
                old_total_cost = float(holding.avg_price) * holding.available_qty
                new_cost = float(final_price) * order.quantity
                new_total_qty = holding.available_qty + order.quantity
                
                holding.avg_price = (old_total_cost + new_cost) / new_total_qty
                holding.available_qty = new_total_qty
            else:
                # 새 보유 종목 추가
                new_holding = Holding(
                    user_id=order.user_id,
                    ticker_code=order.ticker_code,
                    available_qty=order.quantity,
                    avg_price=final_price
                )
                db.session.add(new_holding)
        
        elif order.order_type == OrderType.SELL:
            if holding:
                # 현금 증가 (현재가 기준)
                user.cash += total_price
                
                # 예수금(투자금) 감소 (기존 매매가 기준 차감으로 투자 원금 회수 처리)
                # 만약 전체 수량을 다 파는게 아니라면 부분 차감
                cost_basis = float(holding.avg_price) * order.quantity
                user.deposit -= cost_basis

                # 매도 시 frozen_qty 차감 (Trading에서 동결시켰다고 가정)
                holding.frozen_qty -= order.quantity
                
                # 만약 보유 수량이 0이 되면 관리 필요 (여기서는 수량만 차감)
                if holding.available_qty + holding.frozen_qty == 0:
                    # 필요시 삭제하거나 유지
                    pass
        
        # 매도의 경우 문광명(Trading)님이 주문 접수 시 이미 holdings에서 수량을 frozen 시켰을 확률이 높음.
        # 여기서는 체결 확정 로그만 남기는 것으로 설계.
