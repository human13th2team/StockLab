from flask import Flask
from app.extensions import db, migrate, scheduler
from config import config_by_name

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # DB 및 Migrate 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Scheduler 초기화 및 시작
    scheduler.init_app(app)
    
    # 워커 등록 (임포트 시 데코레이터에 의해 스케줄러에 등록됨)
    with app.app_context():
        from app.features.execution import worker
        
    if not scheduler.running:
        scheduler.start()
    
    # 모델 등록 (마이그레이션을 위해 모든 모델 로드)
    from app import models
    
    # Blueprint 등록
    from app.features.auth import auth_bp
    from app.features.market import market_bp
    from app.features.trading import trading_bp
    from app.features.execution import execution_bp
    from app.features.analysis import analysis_bp
    from app.features.main import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(market_bp, url_prefix='/api/stocks')
    app.register_blueprint(trading_bp, url_prefix='/api/orders')
    app.register_blueprint(execution_bp, url_prefix='/api/executions')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(main_bp)
    
    return app
