from flask import jsonify, request
from . import market_bp

@market_bp.route('/api/stocks/<int:code>/search', methods=['GET'])
def search_stocks():
    query = request.args.get('q', '')
    return jsonify([{"ticker_code": "005930", "name": "삼성전자"}])