import json
import os
import requests

from app.extensions import db, scheduler, redis_client, socketio
from app.features.execution.services import ExecutionService
from app.models.order import Order, OrderStatus
from app.api_clients.rest_api.stock_info_service import StockInfoService
import threading
import traceback

def process_message(app, message):
    """메시지를 받아서 DB 처리 및 Socket.IO 전송"""
    try:
        data = json.loads(message['data'])
        ticker_code = data.get('ticker_code')
        current_price = data.get('current_price')
        if ticker_code and current_price:
            print(f"📡 [Worker] Received: {ticker_code} -> {current_price}")
            
            # [Mock Variation] 개발 모드에서 시각적 확인을 위해 리얼하게 변동성 부여
            import random
            mock_price = current_price + random.randint(-5, 5)
            
            with app.app_context():
                # 1. 미체결 주문 체결 체크
                executions = ExecutionService.check_and_execute_orders(ticker_code, current_price)
                
                # [NEW] 체결 알림 발생
                for exec_info in executions:
                    user_id = exec_info.get('user_id')
                    socketio.emit('order_executed', exec_info, room=f"user_{user_id}", namespace='/')
                    print(f"🎉 [SocketIO] Emitted 'order_executed' to room 'user_{user_id}': {exec_info['message']}")

                # 2. 브로드캐스트 (네임스페이스 명시 및 필드 보정)
                socketio.emit('price_update', {
                    'ticker_code': ticker_code,
                    'price': mock_price,
                    'current_price': current_price,
                    'open': data.get('open'),
                    'high': data.get('high'),
                    'low': data.get('low')
                }, namespace='/')
                print(f"📢 [SocketIO] Broadcasted 'price_update' to '/': {ticker_code} -> {mock_price}")
                
                # DB 세션 명시적 반환 (Windows/Threading 대응)
                db.session.remove()
    except Exception as e:
        print(f"[Redis Worker] Error processing message: {e}")
        traceback.print_exc()

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
