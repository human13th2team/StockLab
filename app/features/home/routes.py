from flask import render_template
from . import home_bp
from .services import home_service

@home_bp.route('', methods=['GET'])
def get_homepage():
    return render_template(
        "features/home/index.html",
        stocks=home_service.get_stock_list(),
        current_time=home_service.get_current_time()
    )
