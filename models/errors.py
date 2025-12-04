from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str = ""
    status_code: int
    message: str
