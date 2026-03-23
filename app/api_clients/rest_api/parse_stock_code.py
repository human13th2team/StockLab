import sys, os
import time

sys.path.insert(0, "/")
import asyncio

import pandas as pd
import requests


from app.api_clients.auth.auth_to_redis import get_access_token_from_redis

API_LIMIT = 20
TOTAL_REQUEST = 785
SLEEP_TIME = 30

# 종목 코드만 추출
stock_codes = pd.read_csv(os.path.join(os.path.dirname(__file__), "st_code.csv"), dtype=str)
stock_codes.columns = ["code", "name"]
code_list = list(stock_codes.code)

# 고정값 준비
authorization = "Bearer " + get_access_token_from_redis()
appkey = os.getenv('KIS_APP_KEY')
appsecret = os.getenv('KIS_APP_SECRET')
base_url = os.getenv('IMMINATION_DOMAIN')
api_url = base_url + "/uapi/domestic-stock/v1/quotations/inquire-price"

# api 요청 보내기와 response 파싱의 비동기 처리
api_header = {
    "content-type": "application/json; charset=utf-8",
    "authorization": authorization,
    "appkey": appkey,
    "appsecret": appsecret,
    "tr_id": "FHKST01010100",
    "custtype": "P"
}

# code_list를 돌면서 list 20개를 보낸다
list_index = 0
def request_inquire_price():
    global list_index
    batch_size = min(API_LIMIT, len(code_list) - list_index)
    responses = []
    for i in range(batch_size):
        res = requests.get(api_url, headers=api_header, params={
            "FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code_list[list_index + i]
        })
        responses.append(res)
        time.sleep(0.5)
    list_index += batch_size
    return responses

# 20개의 요청에서 "stck_shrn_iscd", "hts_avls"를 저장한다
parsed_list = []
async def parse_responses(responses):
    global parsed_list
    parsed = []
    for res in responses:
        data = res.json()["output"]
        parsed.append((data["stck_shrn_iscd"], int(data["hts_avls"])))
    parsed_list.extend(parsed)


async def main():
    while list_index < len(code_list):
        responses = request_inquire_price()
        await asyncio.gather(
            parse_responses(responses),
            asyncio.sleep(30)
        )

    sorted_list = sorted(parsed_list, key=lambda x: x[1], reverse=True)
    print(sorted_list[0:20])


if __name__ == "__main__":
    asyncio.run(main())