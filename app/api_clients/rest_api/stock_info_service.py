import csv
import os
from app.models.stock import Stock
from app.extensions import db

class StockInfoService:
    @staticmethod
    def _get_csv_path():
        # st_code.csv는 이 파일과 같은 디렉토리에 있음
        return os.path.abspath(os.path.join(os.path.dirname(__file__), 'st_code.csv'))

    @staticmethod
    def get_stock_code_by_name(stock_name):
        # 1. DB 우선 검색
        row = Stock.query.filter(Stock.name == stock_name).first()
        if not row:
            row = Stock.query.filter(Stock.name.contains(stock_name)).first()
        
        if row: return row.ticker_code

        # 2. CSV 파일 검색 (Fallback)
        csv_path = StockInfoService._get_csv_path()
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row_data in reader:
                    if len(row_data) < 2: continue
                    code, name = row_data[0], row_data[1]
                    if stock_name in name:
                        # 찾으면 DB에 자동 등록
                        StockInfoService._add_to_db(code, name)
                        return code
        return None

    @staticmethod
    def _add_to_db(code, name):
        try:
            if not Stock.query.get(code):
                s = Stock(ticker_code=code, name=name)
                db.session.add(s)
                db.session.commit()
                print(f"✅ [StockInfo] New stock added to DB: {name} ({code})")
        except Exception as e:
            print(f"⚠️ [StockInfo] Failed to add stock: {e}")

    @staticmethod
    def search_all_csv(query):
        """CSV 전체에서 쿼리와 매칭되는 10개 결과 반환"""
        results = []
        csv_path = StockInfoService._get_csv_path()
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row_data in reader:
                    if len(row_data) < 2: continue
                    code, name = row_data[0], row_data[1]
                    if query in code or query in name:
                        results.append({"ticker_code": code, "name": name})
                        if len(results) >= 10: break
        return results

    @staticmethod
    def get_stock_name_by_code(stock_code):
        row = Stock.query.filter(Stock.ticker_code == stock_code).first()
        if row: return row.name
        
        # CSV fallback
        results = StockInfoService.search_all_csv(stock_code)
        for r in results:
            if r['ticker_code'] == stock_code:
                # DB에 추가 후 이름 반환
                StockInfoService._add_to_db(r['ticker_code'], r['name'])
                return r['name']
        return None