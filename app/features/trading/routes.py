from flask import jsonify, request, session
from datetime import datetime, timedelta
from . import trading_bp
from app.extensions import db, scheduler
from app.models.order import Order, OrderStatus, OrderType
from app.models.user import User


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

# ─── 전역 에러 핸들러 (HTML 응답 차단용) ──────────────────────────────
@trading_bp.errorhandler(Exception)
def handle_exception(e):
    """모든 에러를 JSON으로 반환하고 서버 로그에 즉시 출력"""
    print("❌ [Trading API ERROR] ❌")
    print(traceback.format_exc())
    response = jsonify({
        "message": "서버 내부 오류가 발생했습니다.",
        "error": str(e),
        "type": e.__class__.__name__
    })
    response.status_code = 500
    return response


# ─── 주문 접수 ──────────────────────────────────────────────────────────────
@trading_bp.route('', methods=['POST'])
def place_order():
    data = request.get_json()
    if not data:
        return jsonify({"message": "요청 데이터가 없습니다."}), 400

    ticker_code = data.get('ticker_code')
    order_type_str = data.get('order_type', 'BUY').upper()
    price = data.get('price', 0)
    quantity = data.get('quantity', 0)

    if not ticker_code or quantity <= 0 or price <= 0:
        return jsonify({"message": "필수 파라미터가 누락되었거나 잘못되었습니다."}), 400

    # 세션 기반 유저 ID 확인 (user_id 키 사용)
    user_id = session.get('user_id', 1)
    user = User.query.get(user_id)
    if not user:
        # 테스트를 위해 유저가 없으면 즉시 생성 (비밀번호 필드 필수)
        user = User(id=1, nickname="트레이더K", email="test@stocklab.com", cash=100000000, password_hash="dummy_hash")
        db.session.add(user)
        db.session.commit()

    # ── 자산 데이터 무결성 체크 (None 방지) ──────────────────────────
    if user.cash is None: user.cash = 0
    if user.deposit is None: user.deposit = 0

    total_cost = price * quantity

    # 매수 주문: 잔액 확인 후 예수금(deposit) 차감
    if order_type_str == 'BUY':
        if user.cash < total_cost:
            return jsonify({"message": f"잔액이 부족합니다. 현재 잔액: {user.cash:,}원"}), 400
        user.cash -= total_cost
        user.deposit += total_cost

    # ── 종목 데이터 존재 확인 및 자동 생성 ──────────────────────────
    from app.models.stock import Stock, MarketType
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

    # ── 장 마감 시 자동 취소 잡 등록 (에러 발생 시 무시) ──
    expires_at = get_market_close_utc()
    try:
        scheduler.add_job(
            id=f'auto_cancel_order_{order.id}',
            func=auto_cancel_order,
            args=[order.id],
            trigger='date',
            run_date=expires_at,
            replace_existing=True
        )
    except Exception as e:
        print(f"⚠️ [Scheduler] 자동 취소 예약 실패: {e}")

    return jsonify({
        "order_id": order.id,
        "status": order.status.value,
        "ticker_code": order.ticker_code,
        "order_type": order.order_type.value,
        "price": order.target_price,
        "quantity": order.quantity,
        "total_cost": total_cost,
        "expires_at": expires_at.isoformat() + 'Z',
        "message": f"주문이 접수되었습니다. (장 마감 {expires_at.strftime('%H:%M')} 자동취소 예정)"
    }), 201


# ─── 자동 취소 함수 (스케줄러가 호출) ──────────────────────────────────────
def auto_cancel_order(order_id):
    """APScheduler 잡: 30분 후에도 PENDING인 주문을 취소하고 금액 환불"""
    from app import create_app
    # 이미 앱 컨텍스트가 있는 경우를 위해 try/except 처리
    try:
        app = scheduler.app
        with app.app_context():
            _do_cancel(order_id, reason="30분 만기 자동 취소")
    except Exception as e:
        print(f"[AutoCancel] 주문 {order_id} 취소 중 오류: {e}")


def _do_cancel(order_id, reason="수동 취소"):
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

    db.session.commit()
    print(f"[Order] #{order_id} {reason} 완료 (환불: {order.target_price * order.quantity:,}원)")
    return True, reason


# ─── 미체결 주문 조회 ────────────────────────────────────────────────────────
@trading_bp.route('/pending', methods=['GET'])
def get_pending_orders():
    user_id = session.get('user_id', 1)
    now = datetime.utcnow()

    orders = Order.query.filter_by(user_id=user_id, status=OrderStatus.PENDING).all()
    result = []
    market_close = get_market_close_utc()
    for o in orders:
        remaining_sec = max(0, int((market_close - now).total_seconds()))
        result.append({
            "order_id": o.id,
            "ticker_code": o.ticker_code,
            "order_type": o.order_type.value,
            "target_price": o.target_price,
            "quantity": o.quantity,
            "total_cost": o.target_price * o.quantity,
            "created_at": o.created_at.isoformat() + 'Z',
            "expires_at": market_close.isoformat() + 'Z',
            "remaining_seconds": remaining_sec
        })
    return jsonify(result)


# ─── 수동 취소 ───────────────────────────────────────────────────────────────
@trading_bp.route('/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    user_id = session.get('user_id', 1)
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"message": "주문을 찾을 수 없습니다."}), 404
    if order.user_id != user_id:
        return jsonify({"message": "권한이 없습니다."}), 403

    ok, msg = _do_cancel(order_id, reason="사용자 수동 취소")
    if not ok:
        return jsonify({"message": msg}), 400

    # 스케줄러 잡 제거
    try:
        scheduler.remove_job(f'auto_cancel_order_{order_id}')
    except Exception:
        pass

    refund = order.target_price * order.quantity
    return jsonify({
        "message": f"주문 #{order_id}이 취소되었습니다.",
        "refund_amount": refund
    })


# ─── 보유 주식 조회 ────────────────────────────────────────────────────────
@trading_bp.route('/holdings', methods=['GET'])
def get_holdings():
    from app.models.holding import Holding
    from app.models.stock import Stock
    user_id = session.get('user_id', 1)

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
    return jsonify(result)