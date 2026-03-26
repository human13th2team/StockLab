from flask import jsonify, request, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import auth_bp
from .services import AuthService

@auth_bp.route('/signup', methods=['GET'])
def signup_page():
    return render_template('features/auth/signup.html')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    response, status_code = AuthService.signup(data)
    return jsonify(response), status_code

@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('features/auth/login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response, status_code = AuthService.login(data)
    return jsonify(response), status_code

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user_info = AuthService.get_user_info(current_user_id)
    
    if not user_info:
        return jsonify({"msg": "User not found"}), 404
        
    return jsonify(user_info), 200

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    response, status_code = AuthService.update_user_info(current_user_id, data)
    return jsonify(response), status_code

@auth_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_me():
    current_user_id = get_jwt_identity()
    response, status_code = AuthService.delete_user(current_user_id)
    return jsonify(response), status_code

@auth_bp.route('/profile', methods=['GET'])
def profile_page():
    return render_template('features/auth/profile.html')
