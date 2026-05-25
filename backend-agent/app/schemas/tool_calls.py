from typing import Any

from pydantic import BaseModel


class ToolCallRecord(BaseModel):
    tool_name: str
    tool_input: dict
    tool_output: dict | None = None
    status: str = "success"
    latency_ms: int | None = None


class ToolCallResult(BaseModel):
    tool_call_id: str
    tool_name: str
    result: Any