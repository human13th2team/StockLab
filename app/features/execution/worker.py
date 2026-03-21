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

# 기존 APScheduler 작업은 하위 호환성 또는 백업용으로 유지하거나 제거 가능
# 여기서는 실시간 처리를 위해 Redis 구독 방식으로 전환하였으므로 주석 처리하거나 제거 제안
@scheduler.task('interval', id='monitor_prices_backup', seconds=60)
def backup_price_monitor():
    """실시간 구독이 실패할 경우를 대비한 백업 폴링 (주기를 길게 설정)"""
    print("[Worker] 백업 시세 감시 실행 중...")
    # 필요한 경우 기존 monitor_stock_prices() 로직 실행
