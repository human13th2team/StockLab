from flask import jsonify, request
from . import market_bp
from app.api_clients.rest_api.market_data_service import MarketDataService
from app.models.stock import Stock

@market_bp.route('/search', methods=['GET'])
def search_stocks():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    # 1. DB 우선 검색
    stocks = Stock.query.filter(
        (Stock.name.contains(query)) | (Stock.ticker_code.contains(query))
    ).limit(10).all()
    
    db_results = [{"ticker_code": s.ticker_code, "name": s.name} for s in stocks]
    
    # 2. 만약 결과가 5개 미만이면 CSV에서 추가로 검색하여 보완
    if len(db_results) < 5:
        from app.api_clients.rest_api.stock_info_service import StockInfoService
        csv_results = StockInfoService.search_all_csv(query)
        
        # 중복 제거 (ticker_code 기준)
        existing_codes = {r['ticker_code'] for r in db_results}
        for res in csv_results:
            if res['ticker_code'] not in existing_codes:
                db_results.append(res)
                if len(db_results) >= 10: break
    
    return jsonify(db_results)

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
    interval = request.args.get('interval', '1')
    data, status = MarketDataService.get_stock_history(ticker_code, interval)
    return jsonify(data), status
