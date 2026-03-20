"""
KIS(한국투자증권) OAUTH 연동 함수

이 모듈은 KIS API로 접속키를 발급받는다
1. POST /oauth2/Approval
2. POST /oauth2/tokenP

주요 기능:
    - OAuth2 인증 토큰 발급
"""
import dataclasses
import os

import requests
from dotenv import load_dotenv

import kis_dto
load_dotenv()

#1. 웹소켓 접근키
def get_approval_key():
    header_dict = dataclasses.asdict(kis_dto.ApprovalRequestHeader())
    body_dict = dataclasses.asdict(kis_dto.ApprovalRequestBody())
    # print(body_dict)
    res = requests.post(
        "https://openapivts.koreainvestment.com:29443/oauth2/Approval",
        headers=header_dict,
        json=body_dict
    )
    # print(res)
    rescode = res.status_code
    if rescode == 200: # 토큰 정상 발급
        my_approval_key = kis_dto.ApprovalResponseBody(res.json()).approval_key
        # print(my_approval_key)
    else:
        print("Get Approval key fail!\nYou have to check your app!!\n")
        print(f"Failed code: {rescode}")

#2. REST API 접근 토큰
def get_access_token():
    header_dict = dataclasses.asdict(kis_dto.AccessRequestHeader())
    body_dict = dataclasses.asdict(kis_dto.AccessRequestBody())
    res = requests.post(
        "https://openapivts.koreainvestment.com:29443/oauth2/tokenP",
        headers=header_dict,
        json=body_dict
    )
    rescode = res.status_code
    if rescode == 200: # 토큰 정상 발급
        my_access_token = kis_dto.AccessResponseBody(res.json())
        print(my_access_token)
    else:
        print("Get Approval key fail!\nYou have to check your app!!\n")
        print(f"Failed code: {rescode}")

# if __name__ == "__main__":
#     print("--- KIS 토큰 발급 테스트 시작 ---")
#
#     # 1. 웹소켓 키 출력 테스트
#     try:
#         get_approval_key()
#     except Exception as e:
#         print(f"웹소켓 에러: {e}")
#
#     print("\n" + "="*30 + "\n")
#
#     # 2. REST API 토큰 출력 테스트
#     try:
#         get_access_token()
#     except Exception as e:
#         print(f"REST API 에러: {e}")
#   python kis_token.py > 테스트 가능




