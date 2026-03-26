from app.models.stock import Stock
from app.models.stock_daily_data import StockDailyData
from app.extensions import redis_client, db
from sqlalchemy import func
from datetime import datetime, timedelta


class HomeService:
    @staticmethod
    def get_real_time_stock_list():
        stocks = Stock.query.all()
        result = []

        for stock in stocks:
            # 기본 가격 정보 (리스트형)
            price = redis_client.lindex(f"price:{stock.ticker_code}", 0)
            price = int(price.decode('utf-8')) if price else 0

            # 상세 정보 (해시형) - 바이트 디코딩 주의
            raw_info = redis_client.hgetall(f"stock_info:{stock.ticker_code}")
            stock_info = {k.decode('utf-8'): v.decode('utf-8') for k, v in raw_info.items()}

            oprc_vrss = redis_client.get(f"oprc_vrss:{stock.ticker_code}")
            oprc_vrss = oprc_vrss.decode('utf-8') if oprc_vrss else "0.00%"

            result.append({
                "stock_code": stock.ticker_code,
                "stock_name": stock.name,
                "price": price,
                "high_price": int(stock_info.get('high', 0)),
                "low_price": int(stock_info.get('low', 0)),
                "oprc_vrss_rate": oprc_vrss
            })

        result = sorted(result, key=lambda x: x['stock_code'])
        for i, data in enumerate(result):
            data['rank'] = i + 1

        return result

    @staticmethod
    def get_period_stock_list(period):
        end_date = datetime.now().date()
        if period == "1d":
            start_date = end_date - timedelta(days=1)
        elif period == "1w":
            start_date = end_date - timedelta(days=7)
        else:
            start_date = end_date - timedelta(days=30)

        query_result = db.session.query(
            StockDailyData.ticker_code,
            Stock.name.label('stock_name'),
            func.avg(StockDailyData.open_price).label('avg_open'),
            func.avg(StockDailyData.high_price).label('avg_high'),
            func.avg(StockDailyData.low_price).label('avg_low'),
            func.avg(StockDailyData.close_price).label('avg_close')
        ).join(
            Stock, StockDailyData.ticker_code == Stock.ticker_code
        ).filter(
            StockDailyData.stk_date.between(start_date, end_date)
        ).group_by(
            StockDailyData.ticker_code, Stock.name
        ).all()
        
        result = []
        for row in query_result:
            result.append({
                "stock_code": row.ticker_code,
                "stock_name": row.stock_name,
                "open_price": int(row.avg_open) if row.avg_open else 0,
                "high_price": int(row.avg_high) if row.avg_high else 0,
                "low_price": int(row.avg_low) if row.avg_low else 0,
                "close_price": int(row.avg_close) if row.avg_close else 0
            })
            
        return result

    @staticmethod
    def get_stock_list(period="realtime"):
        # "realtime"
        if period == "realtime":
            return HomeService.get_real_time_stock_list()
        # "1d", "1w", "1m"
        else:
            return HomeService.get_period_stock_list(period)


    @staticmethod
    def get_current_time():
        return datetime.now().strftime("%H:%M")
