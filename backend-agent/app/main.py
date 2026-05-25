from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.router import api_router
from app.core.config import settings
from app.core.exception_handlers import (
    business_error_handler,
    request_validation_error_handler,
    unhandled_exception_handler,
)
from app.core.exceptions import BusinessError
from app.core.logging import setup_logging
from app.core.middleware import request_context_middleware
from app.core.modules import get_enabled_modules, register_enabled_modules
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

    # 注册异常处理器
    app.add_exception_handler(BusinessError, business_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[arg-type]

    # 注册中间件
    app.middleware("http")(request_context_middleware)

    # 保留原有 v1 路由
    app.include_router(api_router)

    # 动态注册启用的模块
    enabled_modules = get_enabled_modules()
    register_enabled_modules(app, enabled_modules)

    # 存储启用的模块列表
    app.state.enabled_modules = enabled_modules

    return app


app = create_app()
