from flask import jsonify, request
from . import market_bp
from app.api_clients.rest_api.market_data_service import MarketDataService
from app.models.stock import Stock

@market_bp.route('/search', methods=['GET'])
def search_stocks():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    # DB에서 이름 또는 코드로 검색
    stocks = Stock.query.filter(
        (Stock.name.contains(query)) | (Stock.ticker_code.contains(query))
    ).limit(10).all()
    
    return jsonify([{"ticker_code": s.ticker_code, "name": s.name} for s in stocks])

@market_bp.route('/quote/<ticker_code>', methods=['GET'])
def get_quote(ticker_code):
    data, status = MarketDataService.search_stock_by_code(ticker_code)
    return jsonify(data), status

@market_bp.route('/orderbook/<ticker_code>', methods=['GET'])
def get_orderbook(ticker_code):
    data, status = MarketDataService.get_order_book(ticker_code)
    return jsonify(data), status

@market_bp.route('/history/<ticker_code>', methods=['GET'])
def get_history(ticker_code):
    # 나중에 실제 KIS API의 히스토리 조회로 연결
    return jsonify({"ticker_code": ticker_code, "price_at_date": 70000})
