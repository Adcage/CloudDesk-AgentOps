from typing import Protocol

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import BusinessError


class UserLike(Protocol):
    id: int
    username: str
    email: str


class UserRepositoryProtocol(Protocol):
    def create(self, username: str, email: str) -> UserLike: ...

    def get_by_id(self, user_id: int) -> UserLike | None: ...


class UserService:
    def __init__(self, repo: UserRepositoryProtocol):
        self.repo = repo

    def create_user(self, username: str, email: str) -> UserLike:
        try:
            return self.repo.create(username=username, email=email)
        except IntegrityError as exc:
            raise BusinessError("username or email already exists", code=4002) from exc

    def get_user(self, user_id: int) -> UserLike:
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise BusinessError("user not found", code=4004)
        return user
