from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import BusinessError
from app.core.logging import get_logger

logger = get_logger()


async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None,
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "code": 4220,
            "message": "Validation Error",
            "data": {"errors": jsonable_encoder(exc.errors())},
            "request_id": getattr(request.state, "request_id", None),
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "code": 5000,
            "message": "Internal Server Error",
            "data": None,
            "request_id": getattr(request.state, "request_id", None),
        },
    )
