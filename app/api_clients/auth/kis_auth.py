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

