from flask import jsonify, request
from . import execution_bp
from .services import ExecutionService

@execution_bp.route('', methods=['GET'])
def get_executions():
    # 현재는 인증이 구현되지 않았으므로 임시로 user_id=1 사용
    user_id = 1 
    ticker_code = request.args.get('ticker_code')
    executions = ExecutionService.get_user_executions(user_id, ticker_code)
    
    result = []
    for ex in executions:
        result.append({
            "id": ex.id,
            "ticker_code": ex.ticker_code,
            "final_price": int(ex.final_price),
            "quantity": ex.quantity,
            "created_at": ex.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(result)

@execution_bp.route('/<string:ticker_code>', methods=['GET'])
def get_executions_by_ticker(ticker_code):
    """특정 종목의 체결 내역 조회"""
    user_id = 1
    executions = ExecutionService.get_user_executions(user_id, ticker_code)
    
    result = []
    for ex in executions:
        result.append({
            "id": ex.id,
            "ticker_code": ex.ticker_code,
            "final_price": int(ex.final_price),
            "quantity": ex.quantity,
            "created_at": ex.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(result)
