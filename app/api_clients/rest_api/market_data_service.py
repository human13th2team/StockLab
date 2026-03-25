import dataclasses
import os

import requests

from . import market_data_dto
from app.api_clients.rest_api.stock_info_service import StockInfoService


class MarketDataService:
    @staticmethod
    # 종목 코드 기반으로 정보 찾아오기
    def search_stock_by_code(stock_code):
        """주식 현재가 API 요청"""
        # 필요한 칼럼 리스트
        columns = [
            "stck_prpr",	# 주식 현재가
            "prdy_ctrt",	# 전일 대비율
            "acml_tr_pbmn",	# 누적 거래 대금
            "acml_vol",	    # 누적 거래량
            "stck_hgpr",	# 주식 최고가
            "stck_lwpr",	# 주식 최저가
            "stck_mxpr",	# 주식 상한가
            "stck_llam",	# 주식 하한가
            "hts_avls",	    # HTS 시가총액
        ]
        api_header = dataclasses.asdict(market_data_dto.MarketDataRequestHeader())
        api_query_params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        res = requests.get(
            url=os.getenv('KIS_DOMAIN') + "/uapi/domestic-stock/v1/quotations/inquire-price",
            headers=api_header,
            params=api_query_params
        )
        if res.status_code == 200:
            data = res.json().get('output', {})
            extract_data = {col: data.get(col, "").strip() for col in columns}
            if extract_data['stck_prpr'] == "0":
                return {"error": "없거나 상장폐지된 종목입니다"}, 404
            else:
                extract_data['ticker_code'] = stock_code
                return extract_data, 200
        else:
            return {"error": "/uapi/domestic-stock/v1/quotations/inquire-price 호출 실패"}, res.status_code

    @staticmethod
    def search_stock_by_name(stock_name):
        stock_code = StockInfoService.get_stock_code_by_name(stock_name)

        if not stock_code:
            return {"error": "종목을 찾을 수 없습니다"}, 404
        else:
            return MarketDataService.search_stock_by_code(stock_code)

