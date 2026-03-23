from flask import jsonify, request
from . import execution_bp

@execution_bp.route('', methods=['GET'])
def get_executions():
    return jsonify([{
        "id": 1, 
        "ticker_code": "005930", 
        "final_price": 75000, 
        "quantity": 10, 
        "created_at": "2024-03-20 12:00:00"
    }])

@execution_bp.route('/<int:execution_id>', methods=['GET'])
def get_execution_detail(execution_id):
    return jsonify({"execution_id": execution_id, "details": "..."})
