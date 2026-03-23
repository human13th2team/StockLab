from flask import jsonify, request
from . import admin_bp
from .services import admin_dashboard_service


@admin_bp.route('', methods=['GET'])
def get_admins():
    return jsonify(admin_dashboard_service.get_admin_dashboard)