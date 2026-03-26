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
            "prdy_vrss",    # 전일 대비
            "acml_tr_pbmn",	# 누적 거래 대금
            "acml_vol",	    # 누적 거래량
            "stck_oprc",    # 주식 시가
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
        base_url = os.getenv('IMMITATION_DOMAIN', 'https://openapivts.koreainvestment.com:29443')
        api_url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-price"
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
            error_msg = res_json.get('msg1', 'KIS API 호출 실패')
            print(f"❌ KIS API Error: {error_msg} (rt_cd: {res_json.get('rt_cd')})")
            return {"error": error_msg}, 400

    @staticmethod
    def search_stock_by_name(stock_name):
        stock_code = StockInfoService.get_stock_code_by_name(stock_name)

        if not stock_code:
            return {"error": "종목을 찾을 수 없습니다"}, 404
        else:
            return MarketDataService.search_stock_by_code(stock_code)

    @staticmethod
    def get_order_book(stock_code):
        """KIS API를 통해 호가(Order Book) 정보를 가져옵니다."""
        api_header = dataclasses.asdict(market_data_dto.MarketDataRequestHeader())
        api_header['tr_id'] = "FHKST01010200" # 호가 TR ID
        
        api_query_params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        base_url = os.getenv('IMMITATION_DOMAIN', 'https://openapivts.koreainvestment.com:29443')
        api_url = f"{base_url}/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"
        
        try:
            res = requests.get(api_url, headers=api_header, params=api_query_params)
            res_json = res.json()
            if res.status_code == 200 and res_json.get('rt_cd') == '0':
                return res_json.get('output', {}), 200
            else:
                return {"error": res_json.get('msg1', '호가 조회 실패')}, 400
        except Exception as e:
            return {"error": str(e)}, 500
