from flask import jsonify, request
from . import trading_bp

@trading_bp.route('', methods=['POST'])
def place_order():
    return jsonify({"order_id": 101, "status": "PENDING"})

@trading_bp.route('/pending', methods=['GET'])
def get_pending_orders():
    return jsonify([{"order_id": 101, "ticker_code": "005930", "target_price": 74000}])

@trading_bp.route('/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    return jsonify({"message": f"Order {order_id} Cancelled"})
