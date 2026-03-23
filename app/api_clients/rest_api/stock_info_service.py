from app.models import Stock

class StockInfoService:
    @staticmethod
    def get_stock_code_by_name(stock_name):
        row = Stock.query.filter(Stock.name.contains(stock_name)).first()

        if row:
            return row.ticker_code
        return None

    @staticmethod
    def get_stock_name_by_code(stock_code):
        row = Stock.query.filter(Stock.ticker_code.contains(stock_code)).first()

        if row:
            return row.name
        return None