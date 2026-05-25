from fastapi import Request


def success(
    data: object | None = None,
    message: str = "OK",
    code: int = 0,
    request: Request | None = None,
) -> dict[str, object | None]:
    request_id = None
    if request is not None:
        request_id = getattr(request.state, "request_id", None)
    return {
        "code": code,
        "message": message,
        "data": data,
        "request_id": request_id,
    }


def success_payload(data: object | None = None, message: str = "OK") -> dict:
    """简化的成功响应，返回标准格式"""
    return {
        "code": "OK",
        "message": message,
        "data": data,
        "request_id": None,
    }
