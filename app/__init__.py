from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config_by_name

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # DB 및 Migrate 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 모델 등록 (마이그레이션을 위해 모든 모델 로드)
    from app import models
    
    # Blueprint 등록
    from app.features.auth import auth_bp
    from app.features.market import market_bp
    from app.features.trading import trading_bp
    from app.features.history import history_bp
    from app.features.analysis import analysis_bp
    from app.features.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(market_bp, url_prefix='/api/stocks')
    app.register_blueprint(trading_bp, url_prefix='/api/orders')
    app.register_blueprint(history_bp, url_prefix='/api/executions')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # 메인 페이지
    from app.features.main import main_bp
    app.register_blueprint(main_bp)
    
    # 스케줄러 초기화 및 시작
    from apscheduler.schedulers.background import BackgroundScheduler
    from app.services.admin_service import AdminService
    
    scheduler = BackgroundScheduler()
    # 매주 월요일 오전 9시에 자금 지급 (예시)
    scheduler.add_job(func=AdminService.weekly_funding_job, trigger="cron", day_of_week="mon", hour=9)
    scheduler.start()
    
    return app
