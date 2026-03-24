from flask import jsonify, request
from . import admin_bp
from app.services.admin_service import AdminService

@admin_bp.route('/funding', methods=['POST'])
def funding():
    """
    수동 자금 지급 API
    Body: {"user_id": 1, "amount": 1000000}
    """
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')
    
    if not user_id or not amount:
        return jsonify({"message": "user_id와 amount는 필수입니다."}), 400
        
    new_cash, message = AdminService.add_funding(user_id, amount)
    
    if new_cash is None:
        return jsonify({"message": message}), 404
        
    return jsonify({
        "message": message,
        "new_cash": new_cash
    })
