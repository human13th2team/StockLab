from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
import redis

redis_client = redis.StrictRedis() # 전역 인스턴스, init_app에서 설정 업데이트 예정
jwt = JWTManager()
db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()
socketio = SocketIO(cors_allowed_origins="*")
