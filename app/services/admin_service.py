from app.models.user import User
from app import db
from datetime import datetime

class AdminService:
    @staticmethod
    def add_funding(user_id, amount):
        """
        특정 유저에게 수동으로 자금 지급
        """
        user = User.query.get(user_id)
        if not user:
            return None, "사용자를 찾을 수 없습니다."

        user.cash += int(amount)
        db.session.commit()
        
        return user.cash, "성공적으로 자금이 지급되었습니다."

    @staticmethod
    def weekly_funding_job():
        """
        [Scheduler용] 매주 모든 일반 사용자에게 정기 자금 지급
        """
        # admin이 아닌 일반 사용자(roles=False)에게 지급
        users = User.query.filter_by(roles=False).all()
        funding_amount = 10000000  # 매주 1,000만원 지급 (예시)
        
        count = 0
        for user in users:
            user.cash += funding_amount
            count += 1
        
        try:
            db.session.commit()
            print(f"[{datetime.now()}] Weekly funding completed: {count} users updated.")
        except Exception as e:
            db.session.rollback()
            print(f"[{datetime.now()}] Weekly funding failed: {str(e)}")
