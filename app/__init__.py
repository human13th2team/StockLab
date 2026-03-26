import time

from flask import Flask
from config import config_by_name
from app.extensions import db, migrate, scheduler, jwt

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # DB, Migrate, JWT 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # SocketIO 초기화
    from app.extensions import socketio
    socketio.init_app(app)
    
    # [NEW] SocketIO 이벤트 핸들러 등록
    from . import socket_events
    
    # Redis 초기화
    from app.extensions import redis_client
    redis_client.connection_pool.connection_kwargs.update({
        'host': app.config.get('REDIS_HOST', 'localhost'),
        'port': app.config.get('REDIS_PORT', 6379),
        'db': app.config.get('REDIS_DB', 0),
        'password': app.config.get('REDIS_PASSWORD')
    })

    # Scheduler 초기화 및 시작
    scheduler.init_app(app)
    if not scheduler.running:
        scheduler.start()

    # # import 하게 되면 메모리에 load되어 스케줄 등록 가능
    from app.api_clients import task_schedules
    # 워커 등록 및 실시간 리스너 시작
    with app.app_context():
        from app.api_clients.auth import kis_auth
        kis_auth.get_access_token()
        kis_auth.get_approval_key()
        from app.features.execution import worker
        worker.start_redis_listener(app)
        from app.api_clients.websocket.ws_client import start_websocket_client
        start_websocket_client(app)
        from app.features.home.worker import start_oprc_vrss_listener
        start_oprc_vrss_listener(app)


    # 모델 등록
    from app import models
    
    # Blueprint 등록
    from app.features.auth import auth_bp
    # from app.features.market import market_bp
    from app.features.trading import trading_bp
    from app.features.execution import execution_bp
    from app.features.analysis import analysis_bp
    from app.features.admin import admin_bp
    from app.features.main import main_bp
    from app.features.home import home_bp

    app.register_blueprint(auth_bp, url_prefix='')
    # app.register_blueprint(market_bp, url_prefix='/api/stocks')
    app.register_blueprint(trading_bp, url_prefix='/api/orders')
    app.register_blueprint(execution_bp, url_prefix='/api/executions')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(home_bp, url_prefix='/api/home')
    app.register_blueprint(main_bp)
    
    # 스케줄러 초기화 및 시작 (app.services.admin_service 누락으로 인한 임시 비활성화)
    # from apscheduler.schedulers.background import BackgroundScheduler
    # from app.services.admin_service import AdminService
    
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(func=AdminService.weekly_funding_job, trigger="cron", day_of_week="mon", hour=9)
    # scheduler.start()
    
    return app
