"""微信小程序授权服务"""

from app.core.exceptions import BusinessError


class WechatMiniAuthService:
    def code2session(self, js_code: str) -> dict:
        if not js_code:
            raise BusinessError("js_code is required", status_code=400)

        # Mock 响应
        return {
            "openid": f"mock_openid_{js_code[:8]}",
            "session_key": "mock_session_key",
            "unionid": None,
        }

    def decrypt_user_info(self, encrypted_data: str, iv: str, session_key: str) -> dict:
        # Mock 响应
        return {
            "nickName": "Mock User",
            "avatarUrl": "https://example.com/avatar.png",
            "gender": 0,
            "country": "CN",
            "province": "Beijing",
            "city": "Beijing",
        }
