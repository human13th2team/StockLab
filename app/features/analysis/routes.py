from flask import jsonify, request, render_template
from . import analysis_bp
from app.services.portfolio_service import PortfolioService
from .ai_service import AnalysisAIService

# 서비스 초기화
portfolio_service = PortfolioService()
ai_service = AnalysisAIService()

@analysis_bp.route('/report')
def report():
    return render_template('analysis/report.html')

@analysis_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """내 포트폴리오 현황 조회 (데이터가 없으면 Mock 데이터 반환)"""
    user_id = 1  # 테스트용 고정 ID
    try:
        result = portfolio_service.get_user_portfolio(user_id)
    except Exception:
        result = None

    if not result:
        # Mock 데이터 생성
        result = {
            "user_nickname": "테스터",
            "cash": 15000000.0,
            "deposit": 0.0,
            "total_asset": 28540000.0,
            "total_purchase_amount": 12000000.0,
            "total_current_value": 13540000.0,
            "total_roi": 12.83,
            "holdings": [
                {
                    "ticker_code": "005930",
                    "qty": 100,
                    "avg_price": 72000.0,
                    "current_price": 78500.0,
                    "purchase_amount": 7200000.0,
                    "current_value": 7850000.0,
                    "roi": 9.03
                },
                {
                    "ticker_code": "000660",
                    "qty": 30,
                    "avg_price": 160000.0,
                    "current_price": 189000.0,
                    "purchase_amount": 4800000.0,
                    "current_value": 5670000.0,
                    "roi": 18.13
                }
            ]
        }
    return jsonify(result)

@analysis_bp.route('/ai/recommend', methods=['POST'])
def ai_recommend():
    """LangChain 기반 AI 추천 API (API 키가 없으면 Mock 조언 반환)"""
    user_id = 1
    
    # 1. 포트폴리오 데이터 확보
    try:
        portfolio_data = portfolio_service.get_user_portfolio(user_id)
    except Exception:
        portfolio_data = None

    if not portfolio_data:
        # Mock 데이터 사용
        portfolio_data = {"holdings": [], "total_roi": 12.83}
        
    # 2. LangChain AI 서비스 호출
    try:
        if not ai_service.api_key:
            raise ValueError("No API Key")
        ai_advice = ai_service.get_investment_advice(portfolio_data)
    except Exception:
        # Mock 조언
        ai_advice = "현재 포트폴리오는 삼성전자와 SK하이닉스 등 반도체 대형주 중심의 안정적인 성장을 보이고 있습니다. 전체 수익률 12.83%는 시장 평균을 상회하는 우수한 성과입니다. 다만, 특정 섹터에 비중이 쏠려 있으므로 리스크 분산을 위해 2차전지나 바이오 섹터의 우량주를 일부 편입하는 것을 권장합니다."
    
    return jsonify({
        "status": "success",
        "ai_advice_text": ai_advice
    })
