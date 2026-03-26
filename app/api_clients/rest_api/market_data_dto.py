import os
from dataclasses import dataclass, field

from app.api_clients.auth.kis_auth import get_access_token

@dataclass
class MarketDataRequestHeader:
    content_type: str="application/json; charset=utf-8"
    authorization: str= field(
    default_factory = lambda: "Bearer " + get_access_token()
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


