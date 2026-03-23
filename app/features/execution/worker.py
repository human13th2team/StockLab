from app.extensions import db, scheduler, redis_client
from app.features.execution.services import ExecutionService
from app.models.order import Order, OrderStatus
import json
import threading

def handle_price_update(message):
    """Redis로부터 수신한 가격 데이터를 처리하는 콜백 함수"""
    try:
        # 데이터 형식 예: {"ticker_code": "005930", "current_price": 75000}
        data = json.loads(message['data'])
        ticker_code = data.get('ticker_code')
        current_price = data.get('current_price')
        
        if ticker_code and current_price:
            # Flask App Context 내에서 실행
            from flask import current_app
            with current_app.app_context():
                ExecutionService.check_and_execute_orders(ticker_code, current_price)
    except Exception as e:
        print(f"[Redis Worker] Error processing message: {e}")

def start_redis_listener(app):
    """Redis Pub/Sub 리스너를 별도 스레드에서 시작"""
    def run_listener():
        with app.app_context():
            print("[Redis Worker] 실시간 시세 구독 시작 (channel: price_updates)")
            pubsub = redis_client.pubsub()
            pubsub.subscribe(**{'price_updates': handle_price_update})
            
            # listen()은 블로킹 호출이므로 무한 루프
            for message in pubsub.listen():
                if message['type'] == 'message':
                    # handle_price_update가 이미 콜백으로 등록되어 있음
                    pass

    thread = threading.Thread(target=run_listener, daemon=True)
    thread.start()

