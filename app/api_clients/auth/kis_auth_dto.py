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

    # 1. getter를 직접 선언하는 방법
    # def get_approval_key(self):
    #     return self.approval_key

    # 2. @property를 사용하는 방법
    # 원래 파이썬 클래스의 멤버변수는 언더바가 붙지만
    # 이 클래스는 API의 response이기 때문에 언어바를 붙이지 않았고
    # 함수명을 변수명과 중복되게 할 수 없었음
    @property
    def get_approval_key(self):
        return self.approval_key

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
    access_token_token_expired: str="" # "2026-03-21 15:40:50"
    token_type: str="" # "Bearer"
    expires_in: int=0 # 86400 (seconds)

    @property
    def get_access_token(self):
        return self.access_token
