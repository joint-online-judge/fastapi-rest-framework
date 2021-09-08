from contextvars import ContextVar
from enum import Enum
from typing import Any, Type

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class ErrorCode(str, Enum):
    Success = "Success"
    Error = "Error"
    InternalServerError = "InternalServerError"
    IllegalFieldError = "IllegalFieldError"
    NotFoundError = "NotFoundError"


_error_code_model: ContextVar[Type[ErrorCode]] = ContextVar(
    "error_code_model", default=ErrorCode
)


def register_error_code_model(cls: Type[ErrorCode]) -> Any:
    if issubclass(cls, ErrorCode):
        _error_code_model.set(cls)
    return cls


def get_error_code_model() -> Type[ErrorCode]:
    return _error_code_model.get()


class BizError(Exception):
    def __init__(self, error_code: ErrorCode, error_msg: str = ""):
        self.error_code = error_code
        self.error_msg = error_msg


def business_exception_response(exc: BizError) -> JSONResponse:
    return JSONResponse(
        jsonable_encoder(
            {"error_code": exc.error_code, "error_msg": exc.error_msg, "data": {}}
        ),
        status_code=status.HTTP_200_OK,
    )
