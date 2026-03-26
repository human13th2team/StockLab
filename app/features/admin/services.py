from app.extensions import db
from .admin_dashboard_dto import admin_dashboard_dto, token_status, user_ranking_dto, user_ranking_info_dto, \
    asset_activate_dto
from app.models.user import User
from app.models.holding import Holding
from app.models.stock import Stock
from app.api_clients.auth.kis_auth import get_access_token, get_approval_key
from app.extensions import redis_client, jwt
from sqlalchemy import func, outerjoin, desc, asc
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

class AdminDashboardService:
    """관리자 페이지 정보 제공 서비스"""
    @classmethod
    def get_total_user(cls):
        return User.query.count()

    @classmethod
    def get_token_status(cls, ttl):
        if (ttl < 600):
            return token_status.CRITICAL
        elif (ttl < 3600):
            return token_status.WARNING
        else:
            return token_status.HEALTHY

    @classmethod
    def get_token_info(cls):
        access_ttl = redis_client.ttl('access_token')
        approval_ttl = redis_client.ttl('approval_key')

        return {
            "access_token" : cls.get_token_status(access_ttl),
            "approval_key": cls.get_token_status(approval_ttl)
        }

    @classmethod
    def get_user_ranking(cls):
        # 상위 3명, 하위 3명
        # 현금 + 주식수량*평단가
        # 모든 사용자(User)의 User.cash + Holding.available_qty*Holding.avg_price
        user_ranking_query = db.session.query(
            User.nickname, 
            (User.cash + func.coalesce(func.sum(Holding.available_qty * Holding.avg_price), 0)).label('all_cash')
        ).outerjoin(Holding, User.id == Holding.user_id).group_by(User.id, User.nickname, User.cash)
        # 1. 상위 3명 (자산 내림차순)
        top_rankers = user_ranking_query.order_by(desc('all_cash')).limit(3).all()

        # 2. 하위 3명 (자산 오름차순)
        bottom_rankers = user_ranking_query.order_by(asc('all_cash')).limit(3).all()

        return user_ranking_dto(
            top_users=[
                user_ranking_info_dto(nickname=ranker.nickname, all_cash=int(ranker.all_cash))
                for ranker in top_rankers
            ],
            bottom_users=[
                user_ranking_info_dto(nickname=ranker.nickname, all_cash=int(ranker.all_cash))
                for ranker in bottom_rankers
            ]
        )

    @classmethod
    def get_asset_activate(cls):
        kospi_count = Stock.query.filter_by(
            market_type="KOSPI",
        ).count()
        kosdaq_count = Stock.query.filter_by(
            market_type="KOSDAQ"
        ).count()
        
        return asset_activate_dto(
            is_kospi_activate=True if kospi_count > 0 else False,
            is_kosdaq_activate=True if kosdaq_count > 0 else False
        )

    @classmethod
    def get_admin_dashboard(cls):
        return admin_dashboard_dto(
            total_user_cnt=cls.get_total_user(),
            tokens=cls.get_token_info(),
            rankings=cls.get_user_ranking(),
            asset_activate_status=cls.get_asset_activate()
        )

    @staticmethod
    def admin_renew_access_token():
        redis_client.delete('access_token') 
        result = get_access_token()
        if result:
            return {"success": True, "message": "Access Token 갱신 완료"}
        return {"success": False, "message": "Access Token 갱신 실패"}

    @staticmethod
    def admin_renew_approval_key():
        redis_client.delete('approval_key')
        result = get_approval_key()
        if result:
            return {"success": True, "message": "Approval Key 갱신 완료"}
        return {"success": False, "message": "Approval Key 갱신 실패"}

    @staticmethod
    def is_admin_role():
        # 토큰 내부의 claims에서 roles 정보를 바로 가져옴 (DB 조회 제거)
        claims = get_jwt()
        return claims.get("roles", False)