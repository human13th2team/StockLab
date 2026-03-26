from flask import jsonify, request, session
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
from . import trading_bp
from .services import (
    place_order_service,
    get_pending_orders_service,
    cancel_order_service,
    get_holdings_service
)

# ─── 전역 에러 핸들러 ──────────────────────────────
@trading_bp.errorhandler(Exception)
def handle_exception(e):
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
@jwt_required(optional=True)
def place_order():
    current_user_id = get_jwt_identity()
    user_id = int(current_user_id) if current_user_id else session.get('user_id', 1)
    
    data = request.get_json()
    result, status_code = place_order_service(user_id, data)
    return jsonify(result), status_code

# ─── 미체결 주문 조회 ────────────────────────────────────────────────────────
@trading_bp.route('/pending', methods=['GET'])
@jwt_required(optional=True)
def get_pending_orders():
    current_user_id = get_jwt_identity()
    user_id = int(current_user_id) if current_user_id else session.get('user_id', 1)
    
    result, status_code = get_pending_orders_service(user_id)
    return jsonify(result), status_code

# ─── 수동 취소 ───────────────────────────────────────────────────────────────
@trading_bp.route('/<int:order_id>', methods=['DELETE'])
@jwt_required(optional=True)
def cancel_order(order_id):
    current_user_id = get_jwt_identity()
    user_id = int(current_user_id) if current_user_id else session.get('user_id', 1)
    
    result, status_code = cancel_order_service(user_id, order_id)
    return jsonify(result), status_code

# ─── 보유 주식 조회 ────────────────────────────────────────────────────────
@trading_bp.route('/holdings', methods=['GET'])
@jwt_required(optional=True)
def get_holdings():
    current_user_id = get_jwt_identity()
    user_id = int(current_user_id) if current_user_id else session.get('user_id', 1)
    
    result, status_code = get_holdings_service(user_id)
    return jsonify(result), status_code