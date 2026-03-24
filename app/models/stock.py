from app.extensions import db
import enum

class MarketType(enum.Enum):
    KOSPI = 'KOSPI'
    KOSDAQ = 'KOSDAQ'

class Stock(db.Model):
    __tablename__ = 'stocks'
    
    ticker_code = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    market_type = db.Column(db.Enum(MarketType), nullable=False)

    # 관계 설정
    daily_data = db.relationship('StockDailyData', backref='stock', lazy=True)
    orders = db.relationship('Order', backref='stock', lazy=True)
    holdings = db.relationship('Holding', backref='stock', lazy=True)

    def __repr__(self):
        return f'<Stock {self.ticker_code}: {self.name}>'
