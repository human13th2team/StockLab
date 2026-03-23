import time
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from app.api_clients.auth import kis_auth
except ImportError as e:
    print(f"❌ 임포트 에러: {e}")
    print(f"현재 탐색 경로: {sys.path[0]}")
    sys.exit(1)

def run_refresh():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] KIS 토큰 상태 체크 중...")
    try:
        # 기존 로직 호출
        result1 = kis_auth.get_access_token()
        print("✅ 체크 완료", result1)
        result2 = kis_auth.get_approval_key()
        print("✅ 체크 완료", result2)
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    print("🚀 KIS 토큰 무한 갱신 루프 시작 (api_clients/auth 내부 실행)")

    while True:
        run_refresh()
        # 10분마다 실행
        time.sleep(600)