import dataclasses
import os

import requests
from flask import jsonify
from requests import head

import market_data_dto
from app.services.kis.rest.StockInfoService import StockInfoService


class MarketDataService:
    @staticmethod
    def search_stock_by_name(stock_name):
        # stock 테이블에서 이름과 매칭되는 종목코드 찾기
        stock_code = StockInfoService.get_stock_by_name(stock_name)

        if not stock_code:
            return jsonify({"error": "종목을 찾을 수 없습니다"}), 404
        # 종목 코드 기반으로 정보 찾아오기
        # 필요한 칼럼 리스트
        columns = [
            "STCK_PRPR", #주식 현재가
            "PRDY_CTRT", #전일 대비율
            "ACML_TR_PBMN", #누적 거래 대금
            "ACML_VOL", #누적 거래량
            "STCK_HGPR", #주식 최고가
            "STCK_LWPR", #주식 최저가
            "STCK_MXPR", #주식 상한가
            "STCK_LLAM", #주식 하한가
        ]
        api_header = dataclasses.asdict(market_data_dto.MarketDataRequestHeader())
        api_query_params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        res = requests.get(
            "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-price",
            header=api_header,
            params=api_query_params
        )
        if res.status_code == 200:
            data = res.json().get('output', {})
            extract_data = {col: data.get(col, "").strip() for col in columns}
            extract_data['name'] = stock_name
            extract_data['ticker_code'] = stock_code

            return jsonify(extract_data), 200
        else:
            return jsonify({"error": "/uapi/domestic-stock/v1/quotations/inquire-price 호출 실패"}), res.status_code
