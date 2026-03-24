from flask import render_template, request, jsonify
from . import home_bp
from .services import HomeService

@home_bp.route('', methods=['GET'])
def get_homepage():
    period = request.args.get('period', 'realtime')
    return render_template(
        "features/home/index.html",
        stocks=HomeService.get_stock_list(period),
        current_time=HomeService.get_current_time(),
        period=period
    )

