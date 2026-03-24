from flask import jsonify, request, render_template
from . import analysis_bp
from .services import PortfolioService, AnalysisAIService

# 서비스 초기화
portfolio_service = PortfolioService()
ai_service = AnalysisAIService()

@analysis_bp.route('/report')
def report():
    return render_template('analysis/report.html')

@analysis_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """
    내 포트폴리오 현황 조회 (실제 데이터베이스 기반)
    데이터가 없는 경우에도 기본 구조를 반환하여 프론트엔드 오류를 방지함.
    """
    user_id = 1  # 테스트용 고정 ID
    try:
        result = portfolio_service.get_user_portfolio(user_id)
        
        # 이동평균선(MA) 트렌드 데이터 생성 (그래프 시각화용)
        # 실제 데이터가 있으면 이를 기반으로, 없으면 빈 트렌드를 반환
        if not result.get('holdings'):
            result["trend_data"] = {
                "labels": ["-", "-", "-", "-", "-", "현재"],
                "ma5": [0, 0, 0, 0, 0, 0],
                "ma20": [0, 0, 0, 0, 0, 0],
                "ma60": [0, 0, 0, 0, 0, 0]
            }
        else:
            # 실시간 데이터가 있는 경우 가상의 트렌드 (실제 API 부재 시 시뮬레이션)
            # 향후 KisApi에서 과거 데이터를 가져오도록 확장 가능
            result["trend_data"] = {
                "labels": ["10일전", "8일전", "6일전", "4일전", "2일전", "현재"],
                "ma5": [72000, 73500, 75000, 76800, 77500, 78500],
                "ma20": [71000, 71500, 72000, 72800, 73500, 74200],
                "ma60": [70000, 70200, 70500, 70800, 71200, 71500]
            }
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify(result)

@analysis_bp.route('/ai/recommend', methods=['POST'])
def ai_recommend():
    """
    실제 데이터베이스 데이터 기반 AI 추천 API
    """
    user_id = 1
    
    # 1. 포트폴리오 데이터 확보 (실제 DB)
    try:
        portfolio_data = portfolio_service.get_user_portfolio(user_id)
    except Exception as e:
        return jsonify({"status": "error", "message": f"DB 조회 실패: {str(e)}"}), 500

    if not portfolio_data or not portfolio_data.get('holdings'):
        return jsonify({
            "status": "success",
            "ai_advice_text": "현재 보유하신 종목이 없습니다. 분석을 시작하려면 종목을 먼저 매수해 주세요."
        })
        
    # 2. Gemini AI 서비스 호출
    try:
        if not ai_service.api_key:
            return jsonify({
                "status": "warning",
                "ai_advice_text": "AI API 키가 설정되지 않았습니다. .env 파일을 확인해 주세요."
            })
            
        ai_advice = ai_service.get_investment_advice(portfolio_data)
    except Exception as e:
        return jsonify({
            "status": "error",
            "ai_advice_text": f"AI 분석 실패: {str(e)}"
        })
    
    return jsonify({
        "status": "success",
        "ai_advice_text": ai_advice
    })
