from app.extensions import db
from .admin_dashboard_dto import admin_dashboard_dto, token_status, user_ranking_dto, user_ranking_info_dto, \
    asset_activate_dto
from app.models.user import User
from app.models.holding import Holding
from app.models.stock import Stock
from ...api_clients.redis_client import init_redis
from sqlalchemy import func, outerjoin, desc, asc


class admin_dashboard_service:
    """관리자 페이지 정보 제공 서비스"""
    @staticmethod
    def get_total_user():
        return User.query.count()

    @staticmethod
    def get_token_status(ttl):
        if (ttl < 600):
            return token_status.CRITICAL
        elif (ttl < 3600):
            return token_status.WARNING
        else:
            return token_status.HEALTHY

    def get_token_info(self):
        r = init_redis()
        access_ttl = r.ttl('access_token')
        approval_ttl = r.ttl('approval_key')

        return [
            {"access_token" : self.get_token_status(access_ttl)},
            {"approval_key": self.get_token_status(approval_ttl)}
        ]

    @staticmethod
    def get_user_ranking():
        # 상위 3명, 하위 3명
        # 현금 + 주식수량*평단가
        # 모든 사용자(User)의 User.cash + Holding.available_qty*Holding.avg_price
        user_ranking_query = db.session.query(
            User.nickname, # User 테이블에서 가져옴
            (User.cash + func.coalesce(func.sum(Holding.quantity * Holding.current_price), 0)).label('all_cash')
        ).outerjoin(Holding, User.userid == Holding.userid).group_by(User.userid, User.nickname)
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

    @staticmethod
    def get_asset_activate():
        kospi_count = Stock.query.filter_by(
            market_type="KOSPI",
        ).count()
        kosdaq_count = Stock.query.filter_by(
            market_type="KOSDAQ"
        )
        # print("짝수" if num % 2 == 0 else "홀수")
        return asset_activate_dto(
            is_kospi_activate=True if kospi_count > 0 else False,
            is_kosdaq_activate=True if kospi_count > 0 else False
        )

    def get_admin_dashboard(self):
        return admin_dashboard_dto(
            total_user_cnt=self.get_total_user(),
            tokens=self.get_token_info(),
            rankings=self.get_user_ranking(),
            asset_activate_status=self.get_asset_activate()
        )


