from flask import jsonify, render_template
from . import admin_bp
from .services import admin_dashboard_service

@admin_bp.route('', methods=['GET'])
def get_admins():
    return jsonify(admin_dashboard_service().get_admin_dashboard().model_dump(mode='json'))

@admin_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    return render_template('features/admin/dashboard.html')

@admin_bp.route('/renewal/access-token', methods=['POST'])
def renew_access_token():
    return jsonify(admin_dashboard_service.admin_renew_access_token())

@admin_bp.route('/renewal/approval-key', methods=['POST'])
def renew_approval_key():
    return jsonify(admin_dashboard_service.admin_renew_approval_key())