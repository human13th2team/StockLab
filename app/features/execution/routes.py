from flask import jsonify, request, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import execution_bp
from .services import ExecutionService
from app.models.order import Order, OrderStatus
from app.models.stock import Stock

@execution_bp.route('', methods=['GET'])
@jwt_required(optional=True)
def get_executions():
    current_user_id = get_jwt_identity()
    user_id = int(current_user_id) if current_user_id else session.get('user_id', 1)
    
    ticker_code = request.args.get('ticker_code')
    executions = ExecutionService.get_user_executions(user_id, ticker_code)
    
    result = []
    for ex in executions:
        result.append({
            "id": ex.id,
            "order_id": ex.order_id,
            "ticker_code": ex.ticker_code,
            "final_price": int(ex.final_price),
            "quantity": ex.quantity,
            "created_at": ex.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(result)

@execution_bp.route('/history', methods=['GET'])
@jwt_required(optional=True)
def get_order_history():
    """유저의 전체 주문 내역 (체결 정보 포함) 조회"""
    current_user_id = get_jwt_identity()
    user_id = int(current_user_id) if current_user_id else session.get('user_id', 1)
    
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    
    result = []
    for order in orders:
        stock = Stock.query.get(order.ticker_code)
        order_data = {
            "id": order.id,
            "ticker_code": order.ticker_code,
            "stock_name": stock.name if stock else "알 수 없음",
            "order_type": order.order_type.value,
            "target_price": int(order.target_price),
            "quantity": order.quantity,
            "status": order.status.value,
            "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "execution": None
        }
        
        if order.execution:
            order_data["execution"] = {
                "id": order.execution.id,
                "final_price": int(order.execution.final_price),
                "quantity": order.execution.quantity,
                "created_at": order.execution.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        result.append(order_data)
        
    return jsonify(result)

@execution_bp.route('/<string:ticker_code>', methods=['GET'])
@jwt_required(optional=True)
def get_executions_by_ticker(ticker_code):
    """특정 종목의 체결 내역 조회"""
    current_user_id = get_jwt_identity()
    user_id = int(current_user_id) if current_user_id else session.get('user_id', 1)
    
    executions = ExecutionService.get_user_executions(user_id, ticker_code)
    
    result = []
    for ex in executions:
        result.append({
            "id": ex.id,
            "ticker_code": ex.ticker_code,
            "final_price": int(ex.final_price),
            "quantity": ex.quantity,
            "created_at": ex.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(result)
