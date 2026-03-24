from pydantic import BaseModel
from enum import Enum
class token_status(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"

class user_ranking_info_dto(BaseModel):
    nickname: str
    all_cash: int

class user_ranking_dto(BaseModel):
    top_users: list[user_ranking_info_dto]
    bottom_users: list[user_ranking_info_dto]

class asset_activate_dto(BaseModel):
    # stocks.market_type에 있는 자산만 true
    is_kospi_activate: bool=True
    is_kosdaq_activate: bool=False

class admin_dashboard_dto(BaseModel):
    # 회원 수
    total_user_cnt: int=0
    # 토큰 [token_name, {status, ttl_seconds}
    tokens: dict[str, token_status]
    # 랭킹정보
    rankings: user_ranking_dto
    # 서비스에서 주는 초기 투자금
    service_seed_money: int=1000000
    # 자산군 상태
    asset_activate_status: asset_activate_dto
