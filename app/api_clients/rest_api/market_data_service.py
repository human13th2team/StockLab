import dataclasses
import os
import requests
import json

from . import market_data_dto
from app.api_clients.rest_api.stock_info_service import StockInfoService
from app.api_clients.redis_client import init_redis
redis_client = init_redis()


class MarketDataService:
    @staticmethod
    # 종목 코드 기반으로 정보 찾아오기
    def search_stock_by_code(stock_code):
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
            api_url,
            headers=api_header,
            params=api_query_params
        )
        res_json = res.json()
        if res.status_code == 200 and res_json.get('rt_cd') == '0':
            data = res_json.get('output', {})
            extract_data = {col: data.get(col, "").strip() if data.get(col) else "0" for col in columns}
            
            if not extract_data.get('stck_prpr') or extract_data['stck_prpr'] == "0":
                return {"error": "데이터가 없거나 잘못되었습니다."}, 404
            
            extract_data['ticker_code'] = stock_code
            
            # 실시간 시세 브로드캐스트를 위해 Redis 발행
            try:
                message = {
                    "ticker_code": stock_code,
                    "current_price": int(extract_data['stck_prpr'])
                }
                redis_client.publish("price_updates", json.dumps(message))
            except Exception as e:
                print(f"⚠️ Failed to publish price update for {stock_code}: {e}")

            return extract_data, 200
        else:
            error_msg = res_json.get('msg1', 'KIS API 호출 실패')
            msg_code = res_json.get('msg_cd', 'No message code')
            print(f"[Error] KIS API Error for {stock_code}: {error_msg} (rt_cd: {res_json.get('rt_cd')}, msg_cd: {msg_code}, http: {res.status_code})")
            
            # KIS API 실패 시 Redis에서 가상/최신 시세 확인 (Mock 모드 지원)
            last_price = redis_client.lindex(f"price:{stock_code}", 0)
            if last_price:
                print(f"[Success] [MarketData] Falling back to Redis price for {stock_code}: {last_price}")
                return {
                    "stck_prpr": str(last_price),
                    "prdy_ctrt": "0.00",
                    "prdy_vrss": "0",
                    "acml_vol": "0",
                    "ticker_code": stock_code,
                    "mock": True
                }, 200
                
            return {"error": error_msg}, 400

    @staticmethod
    def search_stock_by_name(stock_name):
        # stock 테이블에서 이름과 매칭되는 종목코드 찾기
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

    @staticmethod
    def get_stock_history(stock_code, interval='1'):
        """종목의 히스토리 데이터를 가져옵니다. (Mock/Redis 우선)"""
        prices = redis_client.lrange(f"price:{stock_code}", 0, 99)
        if not prices:
            return [], 200
            
        # 최신 데이터가 인덱스 0이므로 뒤집기
        prices = prices[::-1]
        
        import time
        import random
        now = int(time.time())
        step = int(interval) * 60
        now_aligned = (now // step) * step
        
        history = []
        for i, p in enumerate(prices):
            base = int(p)
            timestamp = now_aligned - (len(prices) - 1 - i) * step
            
            # 보다 현실적인 OHLC 데이터 생성
            volatility = base * 0.002 # 0.2% 변동성
            open_p = base + random.uniform(-volatility, volatility)
            close_p = base + random.uniform(-volatility, volatility)
            high_p = max(open_p, close_p) + random.uniform(0, volatility)
            low_p = min(open_p, close_p) - random.uniform(0, volatility)
            
            history.append({
                "time": timestamp,
                "open": round(open_p), 
                "high": round(high_p),
                "low": round(low_p),
                "close": round(close_p),
                "volume": random.randint(1000, 50000)
            })
        return history, 200
