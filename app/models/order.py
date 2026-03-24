from app.extensions import db
from datetime import datetime
import enum

class OrderType(enum.Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class OrderStatus(enum.Enum):
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticker_code = db.Column(db.String(10), db.ForeignKey('stocks.ticker_code'), nullable=False)
    order_type = db.Column(db.Enum(OrderType), nullable=False)
    target_price = db.Column(db.BigInteger, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 관계 설정 (주문 삭제 시 체결 내역도 함께 삭제)
    execution = db.relationship('Execution', backref='order', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id}: {self.order_type} {self.ticker_code}>'
