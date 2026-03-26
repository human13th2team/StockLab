"""
KIS(한국투자증권) OAUTH 연동 함수

이 모듈은 KIS API로 접속키를 발급받는다
1. POST /oauth2/Approval
2. POST /oauth2/tokenP

주요 기능:
    - OAuth2 인증 토큰 발급

ToDo:
    - 서비스 구조로 바꾸기...
"""
import os
import dataclasses
import os

import requests
from dotenv import load_dotenv

from app.api_clients.auth import auth_to_redis, kis_auth_dto

load_dotenv()

def get_approval_key():
    """웹소켓 통신에 사용하는 승인키 상태체크 및 발급"""
    status_ok = auth_to_redis.is_approval_key_ttl_valid()
    if status_ok:
        return auth_to_redis.get_approval_key_from_redis()

    # API 키 존재 여부 확인
    app_key = os.getenv('KIS_APP_KEY')
    app_secret = os.getenv('KIS_APP_SECRET')
    
    if not app_key or not app_secret or app_key == 'your_kis_app_key' or app_secret == 'your_kis_app_secret':
        print("⚠️ KIS API 키가 설정되지 않았습니다. 실시간 시세 기능을 사용할 수 없습니다.")
        return ""

    header_dict = dataclasses.asdict(kis_auth_dto.ApprovalRequestHeader())
    body_dict = dataclasses.asdict(kis_auth_dto.ApprovalRequestBody())
    res = requests.post(
        url=os.getenv('KIS_DOMAIN') + "/oauth2/Approval",
        headers=header_dict,
        json=body_dict
    )
    if res.status_code == 200:
        my_approval_key = kis_auth_dto.ApprovalResponseBody(res.json().get("approval_key"))
        auth_to_redis.store_approval_key(my_approval_key.get_approval_key)
        print("✅ Set Approval key by /oauth2/Approval")
        return my_approval_key.get_approval_key
    else:
        print(f"🐦‍🔥 Get Approval key fail! code: {res.status_code}")
        return ""

def get_access_token():
    """REST API 호출에 사용하는 접근 토큰 상태체크 및 발급"""
    status_ok = auth_to_redis.is_access_token_ttl_valid()
    if status_ok:
        return auth_to_redis.get_access_token_from_redis()

    # API 키 존재 여부 확인
    app_key = os.getenv('KIS_APP_KEY')
    app_secret = os.getenv('KIS_APP_SECRET')
    
    if not app_key or not app_secret or app_key == 'your_kis_app_key' or app_secret == 'your_kis_app_secret':
        return ""

    header_dict = dataclasses.asdict(kis_auth_dto.AccessRequestHeader())
    body_dict = dataclasses.asdict(kis_auth_dto.AccessRequestBody())

    res = requests.post(
        url=os.getenv('KIS_DOMAIN') + "/oauth2/tokenP",
        headers=header_dict,
        json=body_dict
    )
    if res.status_code == 200:
        res_body = res.json()
        my_access_token = kis_auth_dto.AccessResponseBody(
            res_body['access_token'],
            res_body['access_token_token_expired'],
            res_body['token_type'],
            res_body['expires_in']
        )
        auth_to_redis.store_access_token(my_access_token.get_access_token)
        print("✅ Set Access token by /oauth2/tokenP")
        return my_access_token.get_access_token 
    else:
        print(f"🐦‍🔥Get Access token fail! code: {res.json().get('error_description')}")
        return ""

