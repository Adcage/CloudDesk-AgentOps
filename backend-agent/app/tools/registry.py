import httpx

from app.core.config import settings

JAVA_BASE = f"{settings.java_service_url}/api"
INTERNAL_TOKEN = settings.java_internal_token


async def call_internal(
    method: str,
    path: str,
    json: dict | None = None,
    trace_id: str = "",
) -> dict:
    headers = {
        "X-Internal-Token": INTERNAL_TOKEN,
        "X-Correlation-ID": trace_id,
    }
    async with httpx.AsyncClient(base_url=JAVA_BASE, timeout=30.0) as client:
        if method.upper() == "GET":
            resp = await client.get(path, headers=headers, params=json)
        else:
            resp = await client.post(path, headers=headers, json=json)
        resp.raise_for_status()
        return resp.json()