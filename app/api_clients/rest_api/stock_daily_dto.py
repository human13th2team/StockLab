import os
from dataclasses import dataclass, field

from app.api_clients.auth.auth_to_redis import get_access_token_from_redis

@dataclass
class StockDailyRequestHeader:
    content_type: str="application/json; charset=utf-8"
    authorization: str= field(
        default_factory = lambda: "Bearer " + get_access_token_from_redis()
    )
    appkey: str=os.getenv('KIS_APP_KEY')
    appsecret: str=os.getenv('KIS_APP_SECRET')
    tr_id: str="FHKST03010100"
    custtype: str="P"

@dataclass
class StockDailyRequestParams:
    fid_cond_mrkt_div_code: str="J",# J:KRX
    fid_input_iscd: str="035720", # 종목코드 (기본:카카오)
    fid_input_date_1: str="", # 조회 시작일자(YYYYMMDD)
    fid_input_date_2: str="", # 조회 종료일자(YYYYMMDD)
    fid_period_div_code: str="D", # D:일봉 W:주봉, M:월봉, Y:년봉
    fid_org_adj_prc: str="1" # 0:수정주가 1:원주가


@dataclass
class StockDailyResponseBody:
    content_type: str=""
    tr_id: str=""
    tr_cont: str=""