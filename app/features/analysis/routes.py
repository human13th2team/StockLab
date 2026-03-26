from flask import jsonify, request, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import analysis_bp
from .services import PortfolioService, AnalysisAIService, FundingService
from app.extensions import scheduler

# 1. 주간 자금 지급 스케줄러 등록 (매주 월요일 09:00)
@scheduler.task('cron', id='weekly_auto_funding', day_of_week='mon', hour='09', minute='00')
def scheduled_funding():
    with scheduler.app.app_context():
        FundingService.run_weekly_funding(manual=False)

# 2. 서버 재동작 시 미지급분 체크 (모듈 로드 시 실행)
def check_startup_funding():
    try:
        if scheduler.app:
            with scheduler.app.app_context():
                FundingService.run_weekly_funding(manual=True)
    except Exception:
        pass

# 서비스 초기화
portfolio_service = PortfolioService()
ai_service = AnalysisAIService()

# 부팅 시 실행
check_startup_funding()

@analysis_bp.route('/', methods=['GET'])
def report():
    return render_template('features/analysis/report.html', active_menu='report')

@analysis_bp.route('/portfolio', methods=['GET'])
@jwt_required(optional=True)
def get_portfolio():
    """
    내 포트폴리오 현황 조회 (실제 데이터베이스 기반)
    인증된 사용자의 ID를 JWT를 통해 가져옵니다.
    """
    try:
        current_identity = get_jwt_identity()
        user_id = int(current_identity)
        result = portfolio_service.get_user_portfolio(user_id)
        
        print(f"DEBUG: requested user_id={user_id}, type={type(user_id)}")
        result = portfolio_service.get_user_portfolio(user_id)
        print(f"DEBUG: result nickname={result.get('user_nickname')}")
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify(result)

@analysis_bp.route('/ai/recommend', methods=['POST'])
@jwt_required()
def ai_recommend():
    """
    실제 데이터베이스 데이터 기반 AI 추천 API
    인증된 사용자의 ID를 JWT를 통해 가져옵니다.
    """
    try:
        current_identity = get_jwt_identity()
        user_id = int(current_identity)
        
        # 1. 포트폴리오 데이터 확보 (실제 DB)
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
