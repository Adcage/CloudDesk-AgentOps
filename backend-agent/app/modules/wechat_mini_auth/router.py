"""微信小程序授权路由"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.response import success_payload
from app.modules.wechat_mini_auth.service import WechatMiniAuthService

router = APIRouter()
service = WechatMiniAuthService()


class Code2SessionRequest(BaseModel):
    js_code: str


@router.post("/code2session")
def code2session_endpoint(payload: Code2SessionRequest):
    result = service.code2session(payload.js_code)
    return success_payload(result)
