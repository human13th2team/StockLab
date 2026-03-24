import json

from app.extensions import redis_client, socketio
import threading

from app.models import Stock


def handle_oprc_vrss_update(home_msg):
    """소켓으로 데이터를 프론트엔드에 전달하는 함수"""
    try:
        # 주식 종목명 추가
        data = json.loads(home_msg['data'])
        stock_obj = Stock.query.get(data['stock_code'])
        if stock_obj:
            data['stock_name'] = stock_obj.name
            latest_price = redis_client.lindex(f"price:{data['stock_code']}", 0)
            data['price'] = int(latest_price.decode('utf-8')) if latest_price else 0
        else:
            data['stock_name'] = "알 수 없는 종목"
            data['price'] = 0
        socketio.emit('oprc_vrss_update', data)
    except Exception as e:
        print(f"[OPRC_VRSS_UPDATES] 핸들링 에러: {e}")

def start_oprc_vrss_listener(app):
    def run_oprc_vrss_listener():
        with app.app_context():
            pubsub = redis_client.pubsub()
            pubsub.subscribe(**{'oprc_vrss_updates': handle_oprc_vrss_update})

            # 메시지 대기 루프
            for message in pubsub.listen():
                pass

    thread = threading.Thread(target=run_oprc_vrss_listener, daemon=True)
    thread.start()