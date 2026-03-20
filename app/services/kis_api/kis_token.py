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
import kis_dto
import auth_to_redis # ← import

load_dotenv()

def get_approval_key():
    # 캐시된 값 있으면 그거 쓰기
    cached = auth_to_redis.get_approval_key_from_redis()
    if cached:
        return cached.decode()

    header_dict = dataclasses.asdict(kis_dto.ApprovalRequestHeader())
    body_dict = dataclasses.asdict(kis_dto.ApprovalRequestBody())
    res = requests.post(
        "https://openapivts.koreainvestment.com:29443/oauth2/Approval",
        headers=header_dict,
        json=body_dict
    )
    if res.status_code == 200:
        my_approval_key = kis_dto.ApprovalResponseBody(**res.json())
        auth_to_redis.store_approval_key(my_approval_key.approval_key)  # ← 저장
        return my_approval_key.approval_key
    else:
        print(f"Get Approval key fail! code: {res.status_code}")

def get_access_token():
    # 캐시된 값 있으면 그거 쓰기
    cached = auth_to_redis.get_access_token_from_redis()
    if cached:
        return cached.decode()

    header_dict = dataclasses.asdict(kis_dto.AccessRequestHeader())
    body_dict = dataclasses.asdict(kis_dto.AccessRequestBody())
    res = requests.post(
        "https://openapivts.koreainvestment.com:29443/oauth2/tokenP",
        headers=header_dict,
        json=body_dict
    )
    if res.status_code == 200:
        my_access_token = kis_dto.AccessResponseBody(**res.json())
        auth_to_redis.store_access_token(my_access_token.access_token)  # ← 저장
        return my_access_token.access_token
    else:
        print(f"Get Access token fail! code: {res.status_code}")

# if __name__ == "__main__":
#     print("--- KIS 토큰 발급 테스트 ---")
#
#     # 1. 처음 호출 - API 호출 후 Redis 저장
#     token = get_access_token()
#     print(f"토큰: {token}")
#
#     # 2. 두번째 호출 - Redis에서 꺼내옴 (API 호출 안 함)
#     token2 = get_access_token()
#     print(f"캐시된 토큰: {token2}")
#
#     # 같은 값이면 Redis 캐시 정상 동작
#     print(f"동일한 토큰: {token == token2}")