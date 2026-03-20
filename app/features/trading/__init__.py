from flask import Blueprint

trading_bp = Blueprint('trading', __name__)

from . import routes
