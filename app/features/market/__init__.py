from flask import Blueprint

market_bp = Blueprint('market', __name__)

from . import routes
