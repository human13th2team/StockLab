"""
주가변동을 실시간으로 받아오는 모듈입니다

이 모듈은 웹소켓을 통해 실시간으로 두가지 데이터를 구독한다
1. 종목 코드 stck_shrn_iscd
2. 현재 주식 가격 stck_prpr

주요 기능:
    - Redis approval_key 읽고 소켓 연결
    - 소켓으로부터 종목 데이터 받아오기 (모의투자 API, 30개)
        - ws://ops.koreainvestment.com:31000
        - POST /tryitout/H0STCNT0
    - 받은 데이터 파싱해서 종목코드, 현재 주식 가격 return
"""
from flask_socketio import SocketIO, emit

