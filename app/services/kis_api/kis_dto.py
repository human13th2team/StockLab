"""
KIS(한국투자증권) OAUTH 연동 데이터 클래스

이 모듈은 KIS 웹소켓 접속키/접근토큰 발급을 위한 클래스를 선언한다

주요 기능:
    - 웹소켓 접속키 Request/Response -> Approval class
    - 접근토큰 Request/Response -> Access class
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

"""Classes for get APPROVAL KEY."""
@dataclass
class ApprovalRequestHeader:
    content_type: str = "application/json; utf-8"

@dataclass
class ApprovalRequestBody:
    grant_type: str = "client_credentials"
    appkey: str = os.getenv('KIS_APP_KEY')
    secretkey: str = os.getenv('KIS_APP_SECRET')

@dataclass
class ApprovalResponseHeader:
    pass

@dataclass
class ApprovalResponseBody:
    approval_key: str=""

"""Classes for get ACCESS KEY."""
@dataclass
class AccessRequestHeader:
    pass

@dataclass
class AccessRequestBody:
    grant_type: str="client_credentials"
    appkey: str=os.getenv('KIS_APP_KEY')
    appsecret: str=os.getenv('KIS_APP_SECRET')

@dataclass
class AccessResponseHeader:
    pass

@dataclass
class AccessResponseBody:
    access_token: str=""
    token_type: str="" # "Bearer"
    expires_in: float=0.0 # 86400 (seconds)
    access_token_token_expired: str="" # "2026-03-21 15:40:50"