"""
KIS(한국투자증권) 주식 정보 연동 모듈

이 모듈은 Redis에 발급받은 키를 사용하여 주식 정보를 가져온다
1. POST /oauth2/tokenP
2. POST /oauth2/Approval

주요 기능:
    - OAuth2 인증 토큰 발급 및 관리 (유효기간 1일)
    - Redis 저장 후 1일마다 갱신
"""