from flask import Blueprint

history_bp = Blueprint('history', __name__)

from . import routes
