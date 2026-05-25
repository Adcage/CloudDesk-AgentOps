"""认证模块 Schemas"""

from pydantic import BaseModel


class RegisterRequest(BaseModel):
    account: str = ""
    password: str = ""


class LoginRequest(BaseModel):
    account: str = ""
    password: str = ""


class UserResponse(BaseModel):
    id: int
    account: str
    status: str
