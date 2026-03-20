from flask import jsonify, request
from . import analysis_bp

@analysis_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    return jsonify({
        "total_roi": 5.2,
        "holdings": [{"ticker_code": "005930", "avg_price": 72000, "available_qty": 10, "roi": 4.1}]
    })

@analysis_bp.route('/ai/recommend', methods=['POST'])
def ai_recommend():
    return jsonify({"ai_advice_text": "삼성전자 비중을 늘리는 것을 추천합니다."})

@analysis_bp.route('/admin/funding', methods=['POST'])
def admin_funding():
    return jsonify({"new_cash": 150000000})
