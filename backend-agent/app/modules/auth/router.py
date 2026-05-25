"""认证路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success_payload
from app.db.session import get_db
from app.modules.auth.schemas import LoginRequest, RegisterRequest
from app.modules.auth.service import AuthService

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", status_code=201)
def register_user_endpoint(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
):
    user = service.register_user(payload.account, payload.password)
    return success_payload({"id": user.id, "account": user.account})


@router.post("/login")
def login_user_endpoint(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    result = service.login_user(payload.account, payload.password)
    return success_payload(result)


@router.get("/users/{user_id}")
def get_user_endpoint(
    user_id: int,
    service: AuthService = Depends(get_auth_service),
):
    user = service.get_user(user_id)
    return success_payload(
        {
            "id": user.id,
            "account": user.account,
            "status": user.status,
        }
    )
