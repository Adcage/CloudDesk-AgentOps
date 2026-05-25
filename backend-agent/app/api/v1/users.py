from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.response import success
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


def _serialize_user(user) -> dict[str, object]:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    request: Request,
    service: UserService = Depends(get_user_service),
):
    user = service.create_user(payload.username, payload.email)
    return success(_serialize_user(user), request=request)


@router.get("/{user_id}")
def get_user(
    user_id: int,
    request: Request,
    service: UserService = Depends(get_user_service),
):
    user = service.get_user(user_id)
    return success(_serialize_user(user), request=request)
