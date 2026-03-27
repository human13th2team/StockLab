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

        executions_info = []
        for order in pending_orders:
            # 2. 체결 조건 확인 (지정가 매칭)
            is_match = False
            if order.order_type == OrderType.BUY and current_price <= order.target_price:
                is_match = True
            elif order.order_type == OrderType.SELL and current_price >= order.target_price:
                is_match = True

            if is_match:
                ExecutionService._handle_execution(order, current_price)
                
                # [NEW] 알림용 데이터 수집 (사용자 ID, 종목명, 체결가, 수량 등)
                from app.models.stock import Stock
                stock = Stock.query.filter_by(ticker_code=ticker_code).first()
                stock_name = stock.name if stock else ticker_code
                
                executions_info.append({
                    "user_id": order.user_id,
                    "ticker_code": ticker_code,
                    "stock_name": stock_name,
                    "order_type": order.order_type.name, # 'BUY' or 'SELL'
                    "final_price": current_price,
                    "quantity": order.quantity,
                    "message": f"{stock_name} {order.quantity}주가 {current_price:,.0f}원에 {'매수' if order.order_type == OrderType.BUY else '매도'} 체결되었습니다."
                })
        
        if executions_info:
            db.session.commit()
            print(f"[Execution] {ticker_code} 종목 {len(executions_info)}건 체결 완료 (현재가: {current_price})")
        
        return executions_info

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
            # 매수 체결 시: 이미 place_order_service에서 cash -> deposit으로 이동됨.
            order_cost = order.target_price * order.quantity
            actual_cost = final_price * order.quantity
            diff = order_cost - actual_cost
            
            user.deposit = (user.deposit or 0) - order_cost
            if diff > 0:
                user.cash = (user.cash or 0) + diff

            if holding:
                # 평균 단가 및 수량 업데이트
                old_qty = (holding.available_qty or 0) + (holding.frozen_qty or 0)
                old_total_cost = float(holding.avg_price or 0) * old_qty
                new_cost = float(final_price) * order.quantity
                new_total_qty = old_qty + order.quantity
                
                holding.avg_price = (old_total_cost + new_cost) / new_total_qty
                holding.available_qty = (holding.available_qty or 0) + order.quantity
            else:
                # 새 보유 종목 추가
                new_holding = Holding(
                    user_id=order.user_id,
                    ticker_code=order.ticker_code,
                    available_qty=order.quantity,
                    frozen_qty=0,
                    avg_price=final_price
                )
                db.session.add(new_holding)
        
        elif order.order_type == OrderType.SELL:
            if holding:
                # 매도 체결 시: 현금 증가 (체결가 기준)
                user.cash = (user.cash or 0) + total_price
                
                # 매도 주문 시 동결되었던 수량 차감
                holding.frozen_qty = (holding.frozen_qty or 0) - order.quantity
                
                if (holding.available_qty or 0) + (holding.frozen_qty or 0) == 0:
                    db.session.delete(holding)
        
    @staticmethod
    def get_user_executions(user_id, ticker_code=None):
        """사용자의 전체 또는 종목별 체결 내역 조회"""
        query = db.session.query(
            Execution.id,
            Order.ticker_code,
            Execution.final_price,
            Execution.quantity,
            Execution.created_at
        ).join(Order, Execution.order_id == Order.id)\
         .filter(Execution.user_id == user_id)
         
        if ticker_code:
            query = query.filter(Order.ticker_code == ticker_code)
            
        return query.order_by(Execution.created_at.desc()).all()

    @staticmethod
    def get_execution_by_id(execution_id, user_id):
        """특정 체결 상세 내역 조회"""
        return db.session.query(
            Execution.id,
            Order.ticker_code,
            Execution.final_price,
            Execution.quantity,
            Execution.created_at,
            Order.order_type,
            Order.status
        ).join(Order, Execution.order_id == Order.id)\
         .filter(Execution.id == execution_id, Execution.user_id == user_id)\
         .first()
