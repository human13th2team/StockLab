from flask import jsonify, request, render_template
from . import auth_bp

@auth_bp.route('/signup', methods=['POST'])
def signup():
    # 회원가입 및 초기 자금 지급 로직 예정
    return jsonify({"user_id": 1, "nickname": "testuser", "message": "Signup successful with 100M cash"})

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    # 로그인 및 토큰 발급 로직 예정
    return jsonify({"access_token": "dummy-token-12345"})

@auth_bp.route('/me', methods=['GET'])
def me():
    # 내 자산 정보 조회 로직 예정
    return jsonify({
        "nickname": "testuser",
        "cash": 100000000,
        "deposit": 0
    })
