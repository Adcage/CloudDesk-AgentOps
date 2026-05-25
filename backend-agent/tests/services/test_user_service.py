from dataclasses import dataclass

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import BusinessError
from app.services.user_service import UserService


@dataclass
class DummyUser:
    id: int
    username: str
    email: str


class DummyRepo:
    def __init__(self):
        self.items = {}

    def create(self, username, email):
        obj = DummyUser(id=1, username=username, email=email)
        self.items[1] = obj
        return obj

    def get_by_id(self, user_id):
        return self.items.get(user_id)


def test_user_service_create_user_success():
    service = UserService(repo=DummyRepo())
    result = service.create_user("alice", "alice@example.com")
    assert result.username == "alice"


def test_user_service_duplicate_user_raises_business_error():
    class DuplicateRepo:
        def create(self, username, email):
            raise IntegrityError("insert", {"username": username, "email": email}, Exception("dup"))

        def get_by_id(self, user_id):
            return None

    service = UserService(repo=DuplicateRepo())

    with pytest.raises(BusinessError) as exc_info:
        service.create_user("alice", "alice@example.com")

    assert exc_info.value.code == 4002


def test_user_service_user_not_found_raises_business_error():
    service = UserService(repo=DummyRepo())

    with pytest.raises(BusinessError) as exc_info:
        service.get_user(999)

    assert exc_info.value.code == 4004
