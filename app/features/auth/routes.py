from flask import jsonify, request, render_template, session, redirect, url_for
from . import auth_bp

@auth_bp.route('/test-login', methods=['GET'])
def test_login():
    """테스트용 계정으로 즉시 로그인 세션을 생성하며, DB에 유저가 없으면 생성합니다."""
    from app.models.user import User
    from app.extensions import db
    
    user = User.query.get(1)
    if not user:
        # password_hash는 필수 필드이므로 더미 값을 채워넣습니다.
        user = User(id=1, nickname="트레이더K", email="test@stocklab.com", cash=100000000, password_hash="dummy_hash")
        db.session.add(user)
        db.session.commit()
    
    session['user_id'] = 1 # 세션 키 통일
    session['user_nickname'] = "트레이더K"
    
    return redirect('/trading')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    return jsonify({"user_id": 1, "nickname": "트레이더K", "message": "Signup successful with 100M cash"})

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('features/auth/login.html')
    return jsonify({"access_token": "dummy-token-12345"})

@auth_bp.route('/me', methods=['GET'])
def me():
    # 세션에서 유저 정보를 가져오거나 기본값을 반환합니다.
    user = session.get('user_session', {
        "nickname": "게스트",
        "cash": 0
    })
    return jsonify({
        "nickname": user.get('nickname'),
        "cash": 100000000, # 테스트용 1억 원
        "deposit": 0
    })
