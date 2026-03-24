from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class MarketPriceRequestHeader:
    approval_key: str=""
    custtype: str="P"
    tr_type: str="1"
    content_type: str="utf-8"

    def to_dict(self):
        d = asdict(self)
        d["content-type"] = d.pop("content_type")
        return d

@dataclass
class MarketPriceRequestBody:
    tr_id: str="H0STCNT0"
    tr_key: str="035720" # default 카카오

    def wrap_marketprice_request_body(self):
        return {"input": asdict(self)}

@dataclass
class MarketPriceConnectionResponseHeader:
    tr_id: str=""
    tr_key: str=""
    encrypt: str=""

@dataclass
class MarketPriceConnectionResponseBody:
    rt_cd: str=""
    msg_cd: str=""
    msg1: str=""
    output: Optional[dict] = None