"""微信支付服务"""

from uuid import uuid4

from app.core.exceptions import BusinessError


class WechatPayService:
    def create_order(self, amount: int, description: str) -> dict:
        if amount <= 0:
            raise BusinessError("amount must be positive", status_code=400)

        # Mock 预支付
        return {
            "prepay_id": f"wx_{uuid4().hex[:16]}",
            "pay_sign": "mock_sign",
            "time_stamp": "1234567890",
            "nonce_str": uuid4().hex[:16],
        }

    def query_order(self, out_trade_no: str) -> dict:
        # Mock 查询
        return {
            "out_trade_no": out_trade_no,
            "trade_state": "SUCCESS",
            "trade_state_desc": "支付成功",
        }
