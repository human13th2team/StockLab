from flask import Blueprint

api_clients_bp = Blueprint('api_clients', __name__)

from . import routes
