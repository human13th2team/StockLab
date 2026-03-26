from flask import jsonify, request, render_template
from . import admin_bp
from .services import admin_dashboard_service
from app.models.user import User
from app.extensions import db

@admin_bp.route('', methods=['GET'])
def get_admins():
    return jsonify(admin_dashboard_service().get_admin_dashboard().model_dump(mode='json'))

@admin_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    return render_template('features/admin/dashboard.html')

@admin_bp.route('/funding', methods=['POST'])
def manual_funding():
    """
    관리자가 특정 유저에게 수동으로 자금을 지급하는 API
    """
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')
    
    if not user_id or amount is None:
        return jsonify({"status": "error", "message": "user_id와 amount가 필요합니다."}), 400
        
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"status": "error", "message": "사용자를 찾을 수 없습니다."}), 404
            
        # 기존 자금에 합산 (UPDATE)
        user.cash += int(amount)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": f"유저 {user.nickname}에게 {amount}원이 지급되었습니다.",
            "new_cash": int(user.cash)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
