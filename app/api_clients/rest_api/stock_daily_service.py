import os
import time

from app.models.stock_daily_data import StockDailyData
from app.extensions import db
import dataclasses

import requests

from app.api_clients.rest_api import stock_daily_dto
from datetime import datetime

# 국내주식 기간별 시세 API 호출 [start_day:end_day+1] 및 결과 반환
class stock_daily_service:
    @staticmethod
    def call_inquire_daily_itemchartprice(stock_code, start_day, end_day):
        api_header = dataclasses.asdict(stock_daily_dto.StockDailyRequestHeader())
        api_query_params = dataclasses.asdict(stock_daily_dto.StockDailyRequestParams(
            fid_input_iscd=stock_code, # 종목코드 (기본:카카오)
            fid_input_date_1=start_day, # 조회 시작일자(YYYYMMDD)
            fid_input_date_2=end_day, # 조회 종료일자(YYYYMMDD)
        ))
        res = requests.get(
            url=os.getenv('KIS_DOMAIN') + "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            headers=api_header,
            params=api_query_params
        )
        return res

    @staticmethod
    def get_stock_daily(stock_code, is_test=False):
        columns = [
            # output2
            "stck_bsop_date", #날짜
            "stck_oprc", #시가
            "stck_hgpr", #고가
            "stck_lwpr", #저가
            "stck_clpr", #종가
        ] # response에서 필요한 키-값만 지정
        today_yyyymmdd = datetime.today().strftime('%Y%m%d')
        if is_test:
            res = stock_daily_service.call_inquire_daily_itemchartprice(stock_code, "20260225", "20260325")
        else:
            res = stock_daily_service.call_inquire_daily_itemchartprice(stock_code, today_yyyymmdd, today_yyyymmdd)
        if res.status_code == 200:
            # data 타입: LIST
            data = res.json().get('output2')
            for row in data:
                extract_columns = {col: row.get(col, "").strip() for col in columns}
                if extract_columns['stck_oprc'] == "0":
                    return {"error": "없거나 상장폐지된 종목입니다"}, 404
                # stock_daily_data 테이블에 저장
                else:
                    new_stock_daily = StockDailyData(
                        ticker_code = stock_code,
                        stk_date = extract_columns['stck_bsop_date'],
                        open_price = extract_columns['stck_oprc'],
                        high_price = extract_columns['stck_hgpr'],
                        low_price = extract_columns['stck_lwpr'],
                        close_price = extract_columns['stck_clpr'],
                    )
                    db.session.add(new_stock_daily)
                    db.session.commit()
                    time.sleep(0.1) # 유량 조정
            # return f"⛅️ {extract_columns['stck_bsop_date']} {stock_code} data is stored"
        else:
            return f"uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"


