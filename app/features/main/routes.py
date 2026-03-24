from flask import render_template, request
from . import main_bp

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/trading')
def trading():
    ticker = request.args.get('ticker', '005930')
    return render_template('trading/order.html', ticker=ticker)
