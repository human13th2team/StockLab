from app.extensions import db
from app.models.user import User
from flask_jwt_extended import create_access_token

class AuthService:
    @staticmethod
    def signup(data):
        # 필수 필드 확인
        if not all(k in data for k in ('email', 'nickname', 'password')):
            return {"msg": "Missing required fields"}, 400
        
        # 중복 확인
        if User.query.filter_by(email=data['email']).first():
            return {"msg": "Email already exists"}, 400
        if User.query.filter_by(nickname=data['nickname']).first():
            return {"msg": "Nickname already exists"}, 400
        
        # 새 사용자 생성
        user = User(
            email=data['email'],
            nickname=data['nickname'],
            roles=data.get('roles', False)
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return {
            "msg": "User created successfully",
            "user": {
                "email": user.email,
                "nickname": user.nickname,
                "cash": user.cash
            }
        }, 201

    @staticmethod
    def login(data):
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={"roles": user.roles}
            )
            return {
                "access_token": access_token,
                "user": {
                    "nickname": user.nickname,
                    "roles": user.roles
                }
            }, 200
        
        return {"msg": "Invalid email or password"}, 401

    @staticmethod
    def get_user_info(user_id):
        user = db.session.get(User, int(user_id))
        
        if not user:
            return None
            
        return {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "cash": user.cash,
            "deposit": user.deposit,
            "roles": user.roles
        }

    @staticmethod
    def update_user_info(user_id, data):
        user = db.session.get(User, int(user_id))
        
        if not user:
            return {"msg": "User not found"}, 404
            
        if 'email' in data:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return {"msg": "Email already exists"}, 400
            user.email = data['email']
            
        if 'nickname' in data:
            existing_user = User.query.filter_by(nickname=data['nickname']).first()
            if existing_user and existing_user.id != user.id:
                return {"msg": "Nickname already exists"}, 400
            user.nickname = data['nickname']
            
        if 'password' in data:
            user.set_password(data['password'])
            
        db.session.commit()
        
        return {
            "msg": "Profile updated successfully",
            "user": {
                "nickname": user.nickname,
                "email": user.email
            }
        }, 200

    @staticmethod
    def delete_user(user_id):
        user = db.session.get(User, int(user_id))
        
        if not user:
            return {"msg": "User not found"}, 404
            
        try:
            db.session.delete(user)
            db.session.commit()
            return {"msg": "Account deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"msg": f"Server error: {str(e)}"}, 500
