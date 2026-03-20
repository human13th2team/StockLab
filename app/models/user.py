from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    roles = db.Column(db.Boolean, default=False)  # True: Admin, False: User
    cash = db.Column(db.BigInteger, default=100000000)  # 초기 자금 1억
    deposit = db.Column(db.BigInteger, default=0)       # 예수금

    # 관계 설정
    orders = db.relationship('Order', backref='user', lazy=True)
    holdings = db.relationship('Holding', backref='user', lazy=True)
    executions = db.relationship('Execution', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.nickname}>'
