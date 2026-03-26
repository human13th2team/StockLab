from flask import jsonify, render_template
from . import admin_bp
from .services import AdminDashboardService
from flask_jwt_extended import jwt_required

@admin_bp.route('', methods=['GET'])
@jwt_required()
def get_admins():
    if AdminDashboardService.is_admin_role():
        return jsonify(AdminDashboardService.get_admin_dashboard().model_dump(mode='json'))
    return jsonify({"msg": "Admin privilege required"}), 403

@admin_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    # 페이지 렌더링은 허용하고, 실제 데이터 보안은 클라이언트 측 JS와 API에서 담당합니다.
    return render_template('features/admin/dashboard.html')

@admin_bp.route('/renewal/access-token', methods=['POST'])
@jwt_required()
def renew_access_token():
    if AdminDashboardService.is_admin_role():
        return jsonify(AdminDashboardService.admin_renew_access_token())
    return jsonify({"msg": "Admin privilege required"}), 403

@admin_bp.route('/renewal/approval-key', methods=['POST'])
@jwt_required()
def renew_approval_key():
    if AdminDashboardService.is_admin_role():
        return jsonify(AdminDashboardService.admin_renew_approval_key())
    return jsonify({"msg": "Admin privilege required"}), 403
