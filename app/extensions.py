from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from flask_jwt_extended import JWTManager
import redis

db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()
jwt = JWTManager()
redis_client = redis.StrictRedis() # 전역 인스턴스, init_app에서 설정 업데이트 예정
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')
