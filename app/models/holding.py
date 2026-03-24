from app import db

class Holding(db.Model):
    __tablename__ = 'holdings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    ticker_code = db.Column(db.String(10), nullable=False)
    available_qty = db.Column(db.Integer, default=0)
    frozen_qty = db.Column(db.Integer, default=0)
    avg_price = db.Column(db.Numeric(15, 2), default=0.0)

    def __repr__(self):
        return f'<Holding {self.ticker_code}: {self.available_qty}>'
