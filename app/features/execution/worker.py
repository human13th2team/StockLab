from app.extensions import db, scheduler, redis_client, socketio
from app.features.execution.services import ExecutionService
from app.models.order import Order, OrderStatus
import json
import threading

def process_message(app, message):
    """메시지를 받아서 DB 처리 및 Socket.IO 전송"""
    try:
        data = json.loads(message['data'])
        ticker_code = data.get('ticker_code')
        current_price = data.get('current_price')
        
        if ticker_code and current_price:
            print(f"📈 [Redis Worker] 실시간 시세 수신: {ticker_code} -> {current_price}")
            
            with app.app_context():
                # 1. 미체결 주문 체결 체크
                ExecutionService.check_and_execute_orders(ticker_code, current_price)
                
                # 2. 모든 클라이언트에게 실시간 시세 브로드캐스트
                socketio.emit('price_update', {
                    'ticker_code': ticker_code,
                    'price': current_price
                })
                print(f"📣 [SocketIO] Broadcasted price: {ticker_code} -> {current_price}")
    except Exception as e:
        print(f"[Redis Worker] Error processing message: {e}")

def start_redis_listener(app):
    """Redis Pub/Sub 리스너를 별도 스레드에서 시작"""
    def run_listener():
        print("[Redis Worker] 실시간 시세 구독 시작 (channel: price_updates)")
        pubsub = redis_client.pubsub()
        pubsub.subscribe('price_updates')
        
        # listen() 루프에서 직접 처리하여 컨텍스트 유실 방지
        for message in pubsub.listen():
            if message['type'] == 'message':
                process_message(app, message)

    thread = threading.Thread(target=run_listener, daemon=True)
    thread.start()
