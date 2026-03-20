from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_by_name

db = SQLAlchemy()

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # DB 초기화
    db.init_app(app)
    
    # Blueprint 등록 (5대 핵심 기능 분리)
    from app.features.auth import auth_bp
    from app.features.market import market_bp
    from app.features.trading import trading_bp
    from app.features.history import history_bp
    from app.features.analysis import analysis_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(market_bp, url_prefix='/api/stocks')
    app.register_blueprint(trading_bp, url_prefix='/api/orders')
    app.register_blueprint(history_bp, url_prefix='/api/executions')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    
    # 메인 페이지 (UI 진입점)
    from app.features.main import main_bp
    app.register_blueprint(main_bp)
    
    return app
