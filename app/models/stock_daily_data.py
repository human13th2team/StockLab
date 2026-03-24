from app.extensions import db
from datetime import datetime

class StockDailyData(db.Model):
    __tablename__ = 'stock_daily_data'
    
    id = db.Column(db.Integer, primary_key=True)
    ticker_code = db.Column(db.String(10), db.ForeignKey('stocks.ticker_code'), nullable=False)
    stk_date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.BigInteger)
    high_price = db.Column(db.BigInteger)
    low_price = db.Column(db.BigInteger)
    close_price = db.Column(db.BigInteger)

    def __repr__(self):
        return f'<StockDailyData {self.ticker_code} on {self.stk_date}>'
