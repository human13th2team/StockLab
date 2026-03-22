"""
KIS(한국투자증권) OAUTH 연동 함수

이 모듈은 KIS API로 접속키를 발급받는다
1. POST /oauth2/Approval
2. POST /oauth2/tokenP

주요 기능:
    - OAuth2 인증 토큰 발급
"""
import dataclasses

import requests
from dotenv import load_dotenv

import kis_auth_dto
import auth_to_redis

load_dotenv()

def get_approval_key():
    # 캐시된 값 있으면 캐시값 return
    cached = auth_to_redis.get_approval_key_from_redis()
    if cached:
        return cached.decode()

    header_dict = dataclasses.asdict(kis_auth_dto.ApprovalRequestHeader())
    body_dict = dataclasses.asdict(kis_auth_dto.ApprovalRequestBody())
    res = requests.post(
        "https://openapivts.koreainvestment.com:29443/oauth2/Approval",
        headers=header_dict,
        json=body_dict
    )
    if res.status_code == 200:
        my_approval_key = kis_auth_dto.ApprovalResponseBody(res.json())
        auth_to_redis.store_approval_key(my_approval_key.get_approval_key)  # ← 저장
        print("✅ Set Approval key by /oauth2/Approval")
    else:
        print(f"🐦‍🔥 Get Approval key fail! code: {res.status_code}")

def get_access_token():
    # 캐시된 값 있으면 캐시값 return
    cached = auth_to_redis.get_access_token_from_redis()
    if cached:
        return cached.decode()

    header_dict = dataclasses.asdict(kis_auth_dto.AccessRequestHeader())
    body_dict = dataclasses.asdict(kis_auth_dto.AccessRequestBody())

    res = requests.post(
        "https://openapivts.koreainvestment.com:29443/oauth2/tokenP",
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
    else:
        print(f"🐦‍🔥Get Access token fail! code: {res.json().data['error_description']}")

# if __name__ == "__main__":
#     print("--- KIS 발급 테스트 ---")
#
#     token = get_approval_key()
#     print(f"키: {token}")
#
#     token2 = get_access_token()
#     print(f"토큰: {token2}")
