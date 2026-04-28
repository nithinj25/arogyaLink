from pydantic import BaseModel
from typing import Any, Optional


class SuccessResponse(BaseModel):
    status: str = "ok"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    detail: str
    code: Optional[int] = None
