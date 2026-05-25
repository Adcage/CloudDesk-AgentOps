from fastapi import APIRouter, Request

from app.core.response import success

router = APIRouter()


@router.get("/health")
def health(request: Request):
    return success({"status": "ok"}, request=request)
