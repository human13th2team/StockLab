from app.models.stock import Stock
from app.extensions import redis_client
from datetime import datetime


class home_service:

    @staticmethod
    def get_stock_list():
        stocks = Stock.query.all()
        result = []

        for stock in stocks:
            price = redis_client.lindex(f"price:{stock.ticker_code}", 0)
            price = int(price.decode('utf-8')) if price else 0

            oprc_vrss = redis_client.get(f"oprc_vrss:{stock.ticker_code}")
            oprc_vrss = oprc_vrss.decode('utf-8') if oprc_vrss else "0.00%"

            result.append({
                "stock_code": stock.ticker_code,
                "stock_name": stock.name,
                "price": price,
                "oprc_vrss_rate": oprc_vrss
            })

        result = sorted(result, key=lambda x: x['stock_name'])
        for i, data in enumerate(result):
            data['rank'] = i + 1

        return result

    @staticmethod
    def get_current_time():
        return datetime.now().strftime("%H:%M")
