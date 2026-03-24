from flask import jsonify, request
from . import admin_bp
# from app.services.admin_service import AdminService

@admin_bp.route('/funding', methods=['POST'])
def funding():
    """
    수동 자금 지급 API (AdminService 누락으로 임시 비활성화)
    """
    return jsonify({"message": "AdminService가 활성화되지 않았습니다. 분석 기능을 이용해 주세요."}), 503
