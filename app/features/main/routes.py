from flask import render_template, request, session
from flask_jwt_extended import jwt_required, get_jwt_identity
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
        period=period
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
