from flask import render_template, request, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from . import main_bp
from app.models.stock import Stock
from app.features.home.services import HomeService

@main_bp.route('/')
def index():
    period = request.args.get('period', 'realtime')
    return render_template(
        "features/home/index.html",
        stocks=HomeService.get_stock_list(period),
        current_time=HomeService.get_current_time(),
        period=period,
        active_menu='dashboard'
    )

@main_bp.route('/trading')
def trading():
    ticker = request.args.get('ticker', '035420')  # 기본 종목을 네이버로 변경
    stock = Stock.query.get(ticker)
    stock_name = stock.name if stock else '네이버'
    
    # Redis에서 실시간 가격 정보(Hash) 조회
    from app.extensions import redis_client
    # Redis에서 실시간 시가/고가/저가 정보 조회 (bytes -> str 디코딩 처리)
    raw_info = redis_client.hgetall(f"stock_info:{ticker}")
    stock_info = {k.decode('utf-8'): v.decode('utf-8') for k, v in raw_info.items()}
    
    # 템플릿에 전달할 데이터 구성 (문자열인 경우 숫자로 변환)
    price_data = {
        'current': int(stock_info.get('current', 0)),
        'open': int(stock_info.get('open', 0)),
        'high': int(stock_info.get('high', 0)),
        'low': int(stock_info.get('low', 0))
    }
    
    # 전체 종목 리스트 (검색용)
    all_stocks = HomeService.get_stock_list("realtime")
    
    return render_template('features/trading/order.html', 
                          ticker=ticker, 
                          stock_name=stock_name, 
                          price_data=price_data,
                          stocks=all_stocks)

@main_bp.route('/control')
def control():
    """투자 제어 (주문/체결 내역) 화면"""
    return render_template('features/execution/history.html', active_menu='control')

from flask import jsonify

@main_bp.route('/api/stocks/quote/<ticker>')
def get_stock_quote(ticker):
    from app.extensions import redis_client
    raw_info = redis_client.hgetall(f"stock_info:{ticker}")
    if not raw_info:
        return jsonify({"error": "데이터를 불러올 수 없습니다."}), 404
        
    stock_info = {k.decode('utf-8'): v.decode('utf-8') for k, v in raw_info.items()}
    return jsonify(stock_info), 200

@main_bp.route('/api/stocks/history/<ticker>')
def get_stock_history(ticker):
    interval = request.args.get('interval', '1')
    from app.models.stock_daily_data import StockDailyData
    
    # 1일간격(1440분)이 아닐 경우 빈 리스트 반환 (프론트에서 더미 데이터 생성하도록 유도)
    if interval != '1440':
        return jsonify([])

    # 일봉 데이터 조회 (최근 90영업일)
    history = StockDailyData.query.filter_by(ticker_code=ticker)\
                                  .order_by(StockDailyData.stk_date.desc())\
                                  .limit(90).all()
    
    if not history:
        return jsonify([])
        
    # 날짜 오름차순 정렬 (차트 렌더링용)
    history.reverse()
    
    result = []
    for h in history:
        result.append({
            "time": h.stk_date.strftime("%Y-%m-%d"),
            "open": h.open_price,
            "high": h.high_price,
            "low": h.low_price,
            "close": h.close_price
        })
    return jsonify(result), 200
