"""认证仓储层"""

from sqlalchemy.orm import Session

from app.modules.auth.models import UserAuth


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> UserAuth | None:
        return self.db.get(UserAuth, user_id)

    def get_by_account(self, account: str) -> UserAuth | None:
        return self.db.query(UserAuth).filter_by(account=account).first()

    def create(self, account: str, password_hash: str) -> UserAuth:
        user = UserAuth(account=account, password_hash=password_hash)
        self.db.add(user)
        return user
