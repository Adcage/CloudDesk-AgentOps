"""认证服务层"""

from sqlalchemy.orm import Session
from passlib.hash import pbkdf2_sha256

from app.core.exceptions import BusinessError
from app.modules.auth.repository import AuthRepository


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuthRepository(db)

    def register_user(self, account: str, password: str):
        account_value = (account or "").strip()
        password_value = password or ""

        if not account_value or not password_value:
            raise BusinessError("account and password are required", status_code=400)

        existing = self.repo.get_by_account(account_value)
        if existing is not None:
            raise BusinessError("account already exists", status_code=409)

        user = self.repo.create(account_value, pbkdf2_sha256.hash(password_value))
        self.db.commit()
        return user

    def login_user(self, account: str, password: str) -> dict:
        account_value = (account or "").strip()
        password_value = password or ""

        if not account_value or not password_value:
            raise BusinessError("account and password are required", status_code=400)

        user = self.repo.get_by_account(account_value)
        if user is None:
            raise BusinessError("invalid credentials", status_code=401)

        if not pbkdf2_sha256.verify(password_value, user.password_hash):
            raise BusinessError("invalid credentials", status_code=401)

        return {"token": f"demo-token-{user.id}", "user_id": user.id}

    def get_user(self, user_id: int):
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise BusinessError("user not found", status_code=404)
        return user
