import os
import time
import threading
from datetime import datetime
from app import create_app
from app.extensions import socketio, db
from app.models.stock import Stock
from app.api_clients.rest_api.market_data_service import MarketDataService
import json

# Flask-SocketIO와 Windows 환경의 비동기 충돌을 방지하기 위해 표준 스레드 모드로 동작합니다.
config_name = os.environ.get('FLASK_ENV') or 'dev'
app = create_app(config_name)

def heartbeat_task():
    """5초마다 모든 클라이언트에게 heartbeat 이벤트를 전송하여 연결 유지 확인"""
    with app.app_context():
        while True:
            try:
                socketio.emit('heartbeat', {'time': datetime.now().strftime('%H:%M:%S')})
            except Exception as e:
                print(f"Heartbeat error: {e}")
            time.sleep(5)

def realtime_feeder_task():
    """실시간 시세 폴링: KIS REST API를 사용하여 1초마다 시세 업데이트"""
    print("[*] [Feeder] Real-time price feeder (polling) started")
    with app.app_context():
        while True:
            try:
                # DB의 모든 종목 또는 시청 중인 핵심 종목 위주로 조회
                stocks = Stock.query.all()
                if not stocks:
                    time.sleep(5)
                    continue
                
                for stock in stocks:
                    # MarketDataService 내부에서 Redis Publish와 Socket.IO 브로드캐스트가 연동됨
                    MarketDataService.search_stock_by_code(stock.ticker_code)
                    # KIS API 제한 준수 (초당 20건까지 가능하므로 0.2초면 충분히 안전)
                    time.sleep(0.2)
                
                # 전 종목 순회 후 짧게 대기
                time.sleep(1.0)
            except Exception as e:
                print(f"[*] [Feeder] Error: {e}")
                time.sleep(5)
            finally:
                db.session.remove()

if __name__ == '__main__':
    # 하트비트 스레드 시작
    h_thread = threading.Thread(target=heartbeat_task, daemon=True)
    h_thread.start()
    
    # 실시간 시세 피더 스레드 시작 (Polling 방식)
    f_thread = threading.Thread(target=realtime_feeder_task, daemon=True)
    f_thread.start()
    
    port = int(os.environ.get('PORT', 5001))
    print(f"[*] [StockLab] Server started on port {port} (Heartbeat active)")
    
    # allow_unsafe_werkzeug=True는 Windows 환경의 개발 서버 안정성을 위해 추가합니다.
    socketio.run(app, host='0.0.0.0', port=port, use_reloader=False, allow_unsafe_werkzeug=True)
