from flask import Blueprint

auth_bp = Blueprint('kis', __name__)

from . import routes
