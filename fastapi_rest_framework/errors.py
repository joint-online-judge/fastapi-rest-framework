from contextvars import ContextVar
from enum import Enum
from typing import Type

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from fastapi_rest_framework.utils import StrEnumMixin


class ErrorCode(str):
    Success = "Success"
    Error = "Error"
    InternalServerError = "InternalServerError"
    IllegalFieldError = "IllegalFieldError"
    NotFoundError = "NotFoundError"


def _generate_enum(cls: Type[ErrorCode]) -> Enum:
    names = []
    for k, v in cls.__dict__.items():
        if not k.startswith("_"):
            names.append((k, v))
    return Enum(cls.__name__, names=names, type=StrEnumMixin)


_error_code_model: ContextVar[Enum] = ContextVar(
    "error_code_model", default=_generate_enum(ErrorCode)
)


def register_error_code_model(cls: Type[ErrorCode]) -> Enum:
    if issubclass(cls, ErrorCode):
        enum_cls = _generate_enum(cls)
        _error_code_model.set(enum_cls)
        return enum_cls
    raise TypeError(f"{cls} is not subclass of ErrorCode")


def get_error_code_model() -> Enum:
    return _error_code_model.get()


class BizError(Exception):
    def __init__(self, error_code: ErrorCode, error_msg: str = ""):
        self.error_code = str(error_code)
        self.error_msg = error_msg


def business_exception_response(exc: BizError) -> JSONResponse:
    return JSONResponse(
        jsonable_encoder(
            {"error_code": exc.error_code, "error_msg": exc.error_msg, "data": {}}
        ),
        status_code=status.HTTP_200_OK,
    )
