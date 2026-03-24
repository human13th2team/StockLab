# https://apiportal.koreainvestment.com/apiservice-apiservice?/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice
# /uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice
import dataclasses

import requests

from app.api_clients.rest_api import stock_daily_dto
from datetime import datetime

class stock_daily_service:
    @staticmethod
    def call_inquire_daily_itemchartprice(stock_code, start_day, end_day):
        api_header = dataclasses.asdict(stock_daily_dto.StockDailyRequestHeader())
        api_query_params = {
            "fid_input_iscd": stock_code, # 종목코드 (기본:카카오)
            "fid_input_date_1": start_day, # 조회 시작일자(YYYYMMDD)
            "fid_input_date_2": end_day, # 조회 종료일자(YYYYMMDD)
        }
        res = requests.get(
            "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            headers=api_header,
            params=api_query_params
        )
        return res

    @staticmethod
    def get_stock_daily(stock_code):
        columns = [
            # output2
            "stck_bsop_date" #날짜
            "stck_oprc" #시가
            "stck_hgpr" #고가
            "stck_lwpr" #저가
            "stck_clpr" #종가
        ] # response에서 필요한 키-값만 지정
        today_yyyymmdd = datetime.today().strftime('%Y%m%d')
        res = stock_daily_service.call_inquire_daily_itemchartprice(stock_code, today_yyyymmdd, today_yyyymmdd)
        if res.status_code == 200:
            # data 타입: LIST
            data = res.json().get('output2')
            for row in data:
                extract_columns = {col: row.get(col, "").strip() for col in columns}
                if extract_columns['stck_oprc'] == "0":
                    return {"error": "없거나 상장폐지된 종목입니다"}, 404
                else:
                    # stock_daily_data에 저장
                    pass


