from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_by_name

db = SQLAlchemy()

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # DB 초기화
    db.init_app(app)
    
    # Blueprint 등록 (기능별 모듈 등록)
    from app.features.main import main_bp
    from app.features.auth import auth_bp
    from app.features.analysis import analysis_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    
    return app
