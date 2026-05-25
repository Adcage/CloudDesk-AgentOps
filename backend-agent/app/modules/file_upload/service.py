"""文件上传服务"""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.core.exceptions import BusinessError


def _storage_root() -> Path:
    root = Path(settings.storage_root)
    if not root.is_absolute():
        root = Path.cwd() / root
    root.mkdir(parents=True, exist_ok=True)
    return root


def _allowed_extensions() -> set[str]:
    raw = settings.upload_allowed_extensions
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def _max_upload_bytes() -> int:
    return settings.max_upload_size_mb * 1024 * 1024


def parse_scene_mapping() -> dict[str, str]:
    raw = settings.upload_scene_dirs
    mapping: dict[str, str] = {}
    for item in raw.split(","):
        pair = item.strip()
        if not pair or ":" not in pair:
            continue
        scene, scene_dir = pair.split(":", 1)
        scene_name = scene.strip()
        normalized_dir = scene_dir.strip().replace("\\", "/").strip("/")
        if scene_name and normalized_dir:
            mapping[scene_name] = normalized_dir
    if "default" not in mapping:
        mapping["default"] = "uploads"
    return mapping


def validate_upload(scene: str, filename: str, content: bytes):
    if scene not in parse_scene_mapping():
        raise BusinessError("unknown upload scene", status_code=400)

    extension = Path(filename or "").suffix.lower().lstrip(".")
    if extension not in _allowed_extensions():
        raise BusinessError("file extension is not allowed", status_code=400)

    if not content:
        raise BusinessError("file is empty", status_code=400)

    if len(content) > _max_upload_bytes():
        raise BusinessError("file exceeds max upload size", status_code=400)


def save_upload_bytes(scene: str, original_name: str, content: bytes, content_type: str) -> dict:
    scene_value = (scene or "default").strip() or "default"
    mapping = parse_scene_mapping()
    scene_dir = mapping.get(scene_value, "uploads")

    extension = Path(original_name or "").suffix.lower()
    stored_name = f"{uuid4().hex}{extension}"

    relative_path = (
        Path(scene_dir) / f"{datetime.now().year:04d}" / f"{datetime.now().month:02d}" / stored_name
    )

    target = _storage_root() / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)

    return {
        "scene": scene_value,
        "original_name": original_name,
        "stored_name": stored_name,
        "relative_path": relative_path.as_posix(),
        "size": len(content),
        "sha256": sha256(content).hexdigest(),
        "content_type": content_type,
    }


def upload_file(scene: str, filename: str, content: bytes, content_type: str) -> dict:
    scene_value = (scene or "default").strip() or "default"
    validate_upload(scene_value, filename, content)
    return save_upload_bytes(scene_value, filename, content, content_type)
