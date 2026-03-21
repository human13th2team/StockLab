from app.extensions import db, scheduler
from app.features.execution.services import ExecutionService
from app.models.order import Order, OrderStatus
# 팀원 A(탁유제)의 KisApi 또는 공통 함수를 가져와야 함
# 현재는 skeleton이므로 임시 목업 함수 활용 제안
from app.api_clients.kis_api import KisApi

kis_api = KisApi()

def monitor_stock_prices():
    """
    주기적으로 PENDING 주문들을 확인하고 
    현재가와 매칭하여 체결하는 메인 워커 함수
    """
    with scheduler.app.app_context():
        # 1. PENDING 상태인 모든 종목 코드 추출
        pending_tickers = db.session.query(Order.ticker_code).filter_by(
            status=OrderStatus.PENDING
        ).distinct().all()

        for (ticker_code,) in pending_tickers:
            # 2. 현재가 조회 (팀원 A의 API 활용)
            # 실제 구현 시에는 cache(Redis)에서 가져오는 것이 효율적
            current_price = kis_api.get_current_price(ticker_code)
            
            if current_price:
                # 3. 체결 서비스 호출
                ExecutionService.check_and_execute_orders(ticker_code, current_price)

# APScheduler 작업 등록 (예: 5초마다 실행)
@scheduler.task('interval', id='monitor_prices', seconds=5, misfire_grace_time=900)
def scheduled_price_monitor():
    print("[Worker] 시세 감시 워커 가동 중...")
    monitor_stock_prices()
