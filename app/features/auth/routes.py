from flask import jsonify, request, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from . import auth_bp

@auth_bp.route('/signup', methods=['GET'])
def signup_page():
    return render_template('features/auth/signup.html')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    # 필수 필드 확인
    if not all(k in data for k in ('email', 'nickname', 'password')):
        return jsonify({"msg": "Missing required fields"}), 400
    
    # 중복 확인
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "Email already exists"}), 400
    if User.query.filter_by(nickname=data['nickname']).first():
        return jsonify({"msg": "Nickname already exists"}), 400
    
    # 새 사용자 생성 (초기 자금 1억은 모델 기본값으로 자동 설정됨)
    user = User(
        email=data['email'],
        nickname=data['nickname'],
        roles=data.get('roles', False) # 기본값: 일반 유저
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "msg": "User created successfully",
        "user": {
            "email": user.email,
            "nickname": user.nickname,
            "cash": user.cash
        }
    }), 201

@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('features/auth/login.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "access_token": access_token,
            "user": {
                "nickname": user.nickname,
                "roles": user.roles
            }
        }), 200
    
    return jsonify({"msg": "Invalid email or password"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    return jsonify({
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "cash": user.cash,
        "deposit": user.deposit,
        "roles": user.roles
    }), 200

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))
    
    if not user:
        return jsonify({"msg": "User not found"}), 404
        
    data = request.get_json()
    
    # 이메일 수정
    if 'email' in data:
        # 중복 확인 (본인 제외)
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({"msg": "Email already exists"}), 400
        user.email = data['email']
        
    # 닉네임 수정
    if 'nickname' in data:
        # 중복 확인 (본인 제외)
        existing_user = User.query.filter_by(nickname=data['nickname']).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({"msg": "Nickname already exists"}), 400
        user.nickname = data['nickname']
        
    # 비밀번호 수정
    if 'password' in data:
        user.set_password(data['password'])
        
    db.session.commit()
    
    return jsonify({
        "msg": "Profile updated successfully",
        "user": {
            "nickname": user.nickname,
            "email": user.email
        }
    }), 200

@auth_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_me():
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, int(current_user_id))
        
        if not user:
            return jsonify({"msg": "User not found"}), 404
            
        print(f"DEBUG: Attempting to delete user {user.id} ({user.email})")
        
        # 관련 데이터 삭제 (관계 설정에 cascade='all, delete-orphan'이 있어도 수동으로 명시 가능)
        db.session.delete(user)
        db.session.commit()
        
        print(f"DEBUG: User {user.id} deleted successfully")
        return jsonify({"msg": "Account deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Error deleting user: {str(e)}")
        return jsonify({"msg": f"Server error: {str(e)}"}), 500

@auth_bp.route('/profile', methods=['GET'])
def profile_page():
    return render_template('features/auth/profile.html')
