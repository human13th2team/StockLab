from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    roles = db.Column(db.Boolean, default=False)  # True: Admin, False: User
    cash = db.Column(db.BigInteger, default=10000000)  # 초기 자금 100만원
    deposit = db.Column(db.BigInteger, default=0)       # 예수금

    # 관계 설정 (회원 탈퇴 시 연관 데이터 자동 삭제)
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    holdings = db.relationship('Holding', backref='user', lazy=True, cascade='all, delete-orphan')
    executions = db.relationship('Execution', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password_text):
        self.password = generate_password_hash(password_text)

    def check_password(self, password_text):
        return check_password_hash(self.password, password_text)

    def __repr__(self):
        return f'<User {self.nickname}>'
