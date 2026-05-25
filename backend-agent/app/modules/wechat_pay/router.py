"""微信支付路由"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.response import success_payload
from app.modules.wechat_pay.service import WechatPayService

router = APIRouter()
service = WechatPayService()


class CreateOrderRequest(BaseModel):
    amount: int
    description: str = ""


@router.post("/orders")
def create_order_endpoint(payload: CreateOrderRequest):
    result = service.create_order(payload.amount, payload.description)
    return success_payload(result)


@router.get("/orders/{out_trade_no}")
def query_order_endpoint(out_trade_no: str):
    result = service.query_order(out_trade_no)
    return success_payload(result)
