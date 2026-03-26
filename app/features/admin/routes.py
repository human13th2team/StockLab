from flask import jsonify, render_template
from . import admin_bp
from .services import AdminDashboardService
from flask_jwt_extended import jwt_required

@admin_bp.route('', methods=['GET'])
def get_admins():
    return jsonify(AdminDashboardService.get_admin_dashboard().model_dump(mode='json'))

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    if AdminDashboardService.is_admin_role():
        return render_template('features/admin/dashboard.html')
    else:
        return render_template('features/auth/login.html')

@admin_bp.route('/renewal/access-token', methods=['POST'])
def renew_access_token():
    return jsonify(AdminDashboardService.admin_renew_access_token())

@admin_bp.route('/renewal/approval-key', methods=['POST'])
def renew_approval_key():
    return jsonify(AdminDashboardService.admin_renew_approval_key())
