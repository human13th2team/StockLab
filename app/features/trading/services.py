from flask import jsonify, session
from datetime import datetime, timedelta
from app.extensions import db, scheduler
from app.models.order import Order, OrderStatus, OrderType
from app.models.user import User
from app.models.stock import Stock, MarketType
from app.models.holding import Holding
import traceback

def get_market_close_utc():
    """다음 한국 장 마감 시간(15:30 KST = 06:30 UTC)을 계산"""
    now_utc = datetime.utcnow()
    # 15:30 KST는 06:30 UTC입니다.
    close_utc = now_utc.replace(hour=6, minute=30, second=0, microsecond=0)
    if now_utc >= close_utc:
        # 이미 오늘 장이 끝났다면 내일 마감 시간으로 설정
        close_utc += timedelta(days=1)
    return close_utc

def place_order_service(user_id, data):
    ticker_code = data.get('ticker_code')
    order_type_str = data.get('order_type', 'BUY').upper()
    price = int(data.get('price', 0))
    quantity = int(data.get('quantity', 0))

    if not ticker_code or quantity <= 0 or price <= 0:
        return {"message": "필수 파라미터가 누락되었거나 잘못되었습니다."}, 400

    user = User.query.get(user_id)
    if not user:
        # 테스트를 위해 유저가 없으면 즉시 생성
        user = User(id=user_id, nickname="트레이더K", email=f"test{user_id}@stocklab.com", cash=100000000)
        user.set_password("dummy_password")
        db.session.add(user)
        db.session.commit()

    # ── 자산 데이터 무결성 체크 (None 방지) ──────────────────────────
    if user.cash is None: user.cash = 0
    if user.deposit is None: user.deposit = 0

    total_cost = price * quantity

    # 매수 주문: 잔액 확인 후 예수금(deposit) 차감
    if order_type_str == 'BUY':
        if user.cash < total_cost:
            return {"message": f"잔액이 부족합니다. 현재 잔액: {user.cash:,}원"}, 400
        user.cash -= total_cost
        user.deposit += total_cost
    
    # 매도 주문: 보유 주식 확인 후 수량 동결 (frozen_qty)
    elif order_type_str == 'SELL':
        holding = Holding.query.filter_by(user_id=user_id, ticker_code=ticker_code).first()
        if not holding or (holding.available_qty or 0) < quantity:
            available = holding.available_qty if holding else 0
            return {"message": f"매도 가능한 수량이 부족합니다. (현재: {available}주)"}, 400
        
        # 가용 수량 -> 동결 수량 이동
        holding.available_qty -= quantity
        if holding.frozen_qty is None: holding.frozen_qty = 0
        holding.frozen_qty += quantity

    # ── 종목 데이터 존재 확인 및 자동 생성 ──────────────────────────
    stock = Stock.query.get(ticker_code)
    if not stock:
        # 테스트 편의를 위해 종목이 없으면 즉시 생성 (KOSPI/NAVER 기본)
        stock = Stock(ticker_code=ticker_code, name="NAVER", market_type=MarketType.KOSPI)
        db.session.add(stock)
        db.session.commit()

    order = Order(
        user_id=user_id,
        ticker_code=ticker_code,
        order_type=OrderType[order_type_str],
        target_price=price,
        quantity=quantity,
        status=OrderStatus.PENDING
    )
    db.session.add(order)
    db.session.commit()

    # ── 장 마감 시점 자동취소 잡 등록 ──
    expires_at = get_market_close_utc()
    try:
        scheduler.add_job(
            id=f'auto_cancel_order_{order.id}',
            func=auto_cancel_order_task,
            args=[order.id],
            trigger='date',
            run_date=expires_at,
            replace_existing=True
        )
    except Exception as e:
        print(f"⚠️ [Scheduler] 자동 취소 예약 실패: {e}")

    return {
        "order_id": order.id,
        "status": order.status.value,
        "ticker_code": order.ticker_code,
        "order_type": order.order_type.value,
        "price": order.target_price,
        "quantity": order.quantity,
        "total_cost": total_cost,
        "expires_at": expires_at.isoformat() + 'Z',
        "message": f"주문이 접수되었습니다. (장 마감 15:30 자동취소 예정)"
    }, 201

def auto_cancel_order_task(order_id):
    """APScheduler 잡: 장 마감 시점에도 PENDING인 주문을 취소하고 금액/수량 환전"""
    # routes.py에 있던 auto_cancel_order와 동일한 기능
    try:
        app = scheduler.app
        with app.app_context():
            execute_cancel(order_id, reason="30분 만기 자동 취소")
    except Exception as e:
        print(f"[AutoCancel] 주문 {order_id} 취소 중 오류: {e}")

def execute_cancel(order_id, reason="수동 취소"):
    """공통 취소 로직 — 상태 변경 + 금액 환불"""
    order = Order.query.get(order_id)
    if not order or order.status != OrderStatus.PENDING:
        return False, "취소할 미체결 주문이 없습니다."

    order.status = OrderStatus.CANCELLED

    # 매수 주문: 동결된 예수금 → 현금 환불
    if order.order_type == OrderType.BUY:
        refund = order.target_price * order.quantity
        user = User.query.get(order.user_id)
        if user:
            user.deposit -= refund
            user.cash += refund
    
    # 매도 주문: 동결된 주식 → 가용 주식으로 복구
    elif order.order_type == OrderType.SELL:
        holding = Holding.query.filter_by(user_id=order.user_id, ticker_code=order.ticker_code).first()
        if holding:
            holding.frozen_qty -= order.quantity
            holding.available_qty += order.quantity

    db.session.commit()
    print(f"[Order] #{order_id} {reason} 완료 (환불: {order.target_price * order.quantity:,}원)")
    return True, reason

def get_pending_orders_service(user_id):
    now = datetime.utcnow()
    orders = Order.query.filter_by(user_id=user_id, status=OrderStatus.PENDING).all()
    result = []
    for o in orders:
        # 주문 생성 시간 기준이 아닌 장 마감 시점으로 만료 시간 설정
        expires_at = get_market_close_utc()
        remaining_sec = max(0, int((expires_at - now).total_seconds()))
        result.append({
            "order_id": o.id,
            "ticker_code": o.ticker_code,
            "stock_name": o.stock.name if o.stock else "국내주식",
            "order_type": o.order_type.value,
            "target_price": o.target_price,
            "quantity": o.quantity,
            "total_cost": o.target_price * o.quantity,
            "created_at": o.created_at.isoformat() + 'Z',
            "expires_at": expires_at.isoformat() + 'Z',
            "remaining_seconds": remaining_sec
        })
    return result, 200

def cancel_order_service(user_id, order_id):
    order = Order.query.get(order_id)

    if not order:
        return {"message": "주문을 찾을 수 없습니다."}, 404
    if order.user_id != user_id:
        return {"message": "권한이 없습니다."}, 403

    ok, msg = execute_cancel(order_id, reason="사용자 수동 취소")
    if not ok:
        return {"message": msg}, 400

    # 스케줄러 잡 제거
    try:
        scheduler.remove_job(f'auto_cancel_order_{order_id}')
    except Exception:
        pass

    refund = order.target_price * order.quantity
    return {
        "message": f"주문 #{order_id}이 취소되었습니다.",
        "refund_amount": refund
    }, 200

def get_holdings_service(user_id):
    holdings = Holding.query.filter_by(user_id=user_id).all()
    result = []
    for h in holdings:
        stock = Stock.query.get(h.ticker_code)
        if (h.available_qty or 0) + (h.frozen_qty or 0) <= 0:
            continue
            
        result.append({
            "ticker_code": h.ticker_code,
            "stock_name": stock.name if stock else "알 수 없는 종목",
            "available_qty": h.available_qty or 0,
            "frozen_qty": h.frozen_qty or 0,
            "total_qty": (h.available_qty or 0) + (h.frozen_qty or 0),
            "avg_price": float(h.avg_price or 0)
        })
    return result, 200
