from flask import render_template, request
from . import main_bp
from app.models.stock import Stock

@main_bp.route('/')
def index():
    return render_template('features/main/index.html')

@main_bp.route('/trading')
def trading():
    ticker = request.args.get('ticker', '035420')  # 기본 종목을 네이버로 변경
    stock = Stock.query.get(ticker)
    stock_name = stock.name if stock else '네이버'
    return render_template('features/trading/order.html', ticker=ticker, stock_name=stock_name)
