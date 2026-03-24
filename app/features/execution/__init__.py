from flask import Blueprint

execution_bp = Blueprint('execution', __name__)

from . import routes
