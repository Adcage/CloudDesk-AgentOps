"""健康检查路由"""

from fastapi import APIRouter, Request

from app.core.response import success_payload

router = APIRouter()


@router.get("/health")
def health_check(request: Request):
    """健康检查端点"""
    enabled_modules = getattr(request.app.state, "enabled_modules", [])
    return success_payload(
        {
            "status": "healthy",
            "enabled_modules": enabled_modules,
        }
    )
