from app.models import stock

class StockInfoService:
    @staticmethod
    def get_stock_by_name(stock_name):
        row = stock.query.filter(stock.name.contains(stock_name)).first()

        if row:
            return stock.ticker_code
        return None