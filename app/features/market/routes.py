from flask import jsonify, request
from . import market_bp

@market_bp.route('/search', methods=['GET'])
def search_stocks():
    query = request.args.get('q', '')
    return jsonify([{"ticker_code": "005930", "name": "삼성전자"}])

@market_bp.route('/quote/<ticker_code>', methods=['GET'])
def get_quote(ticker_code):
    return jsonify({"ticker_code": ticker_code, "current_price": 75000})

@market_bp.route('/history/<ticker_code>', methods=['GET'])
def get_history(ticker_code):
    return jsonify({"ticker_code": ticker_code, "price_at_date": 70000})
