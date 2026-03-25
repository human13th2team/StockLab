import os
import time
import threading
from datetime import datetime
from app import create_app
from app.extensions import socketio

# Flask-SocketIO와 Windows 환경의 비동기 충돌을 방지하기 위해 표준 스레드 모드로 동작합니다.
config_name = os.environ.get('FLASK_ENV') or 'dev'
app = create_app(config_name)

def heartbeat_task():
    """5초마다 모든 클라이언트에게 heartbeat 이벤트를 전송하여 연결 유지 확인"""
    with app.app_context():
        while True:
            socketio.emit('heartbeat', {'time': datetime.now().strftime('%H:%M:%S')})
            time.sleep(5)

if __name__ == '__main__':
    # 하트비트 스레드 시작
    h_thread = threading.Thread(target=heartbeat_task, daemon=True)
    h_thread.start()
    
    port = int(os.environ.get('PORT', 5001))
    print(f"🚀 [StockLab] Server started on port {port} (Heartbeat active)")
    
    # use_reloader=False는 스레드 안정성을 위해 권장됩니다.
    socketio.run(app, host='0.0.0.0', port=port, use_reloader=False)
