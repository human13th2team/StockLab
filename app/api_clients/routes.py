from flask import jsonify, request
from . import api_clients_bp
from app.api_clients.rest_api.market_data_service import MarketDataService

@api_clients_bp.route('/search', methods=['GET'])
def search_stocks():
    stock_name = request.args.get('q')
    if not stock_name:
        return jsonify({"error": "상품을 찾을 수 없습니다"}), 400

    data, status_code = MarketDataService.search_stock_by_name(stock_name)
    if data:
        return jsonify([data]), status_code
    return jsonify({"error": "종목 코드에 해당하는 상품을 찾을 수 없습니다"}), status_code

@api_clients_bp.route('/daily-price/<string:code>', methods=['GET'])
def daily_price(code):
    data, status_code = MarketDataService.search_stock_by_code(code)
    if status_code == 200:
        return jsonify([data]), 200
    else:
        return jsonify({"error": "종목 코드에 해당하는 상품을 찾을 수 없습니다"}), status_code
