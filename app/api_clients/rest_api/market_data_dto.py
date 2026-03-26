import os
from dataclasses import dataclass, field

from app.api_clients.auth.auth_to_redis import get_access_token_from_redis

@dataclass
class MarketDataRequestHeader:
    content_type: str="application/json; charset=utf-8"
    authorization: str= field(
        default_factory = lambda: "Bearer " + get_access_token_from_redis()
    )
    appkey: str=os.getenv('KIS_APP_KEY')
    appsecret: str=os.getenv('KIS_APP_SECRET')
    tr_id: str="FHKST01010100"
    custtype: str="P"

@dataclass
class MarketDataResponseHeader:
    content_type: str=""
    tr_id: str=""
    tr_cont: str=""


