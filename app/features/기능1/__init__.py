from flask import Blueprint

analysis_bp = Blueprint('analysis', __name__)

from . import routes
