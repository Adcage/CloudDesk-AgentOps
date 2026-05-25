"""文件上传路由"""

from fastapi import APIRouter, File, Form, UploadFile

from app.core.exceptions import BusinessError
from app.core.response import success_payload
from app.modules.file_upload.service import upload_file

router = APIRouter()


@router.post("/upload")
async def upload_file_endpoint(
    file: UploadFile = File(...),
    scene: str = Form(default="default"),
):
    if file.filename is None:
        raise BusinessError("file is required", status_code=400)

    content = await file.read()
    result = upload_file(
        scene=scene,
        filename=file.filename,
        content=content,
        content_type=file.content_type or "",
    )
    return success_payload(result)
