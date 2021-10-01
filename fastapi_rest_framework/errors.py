from contextvars import ContextVar
from enum import Enum
from typing import TYPE_CHECKING, Type, Union

from fastapi import FastAPI, Request, status
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


# TODO: fix code completion
def register_error_code_model(cls: Type[ErrorCode]) -> Type[ErrorCode]:
    if not issubclass(cls, ErrorCode):
        raise TypeError(f"{cls} is not subclass of ErrorCode")
    if TYPE_CHECKING:
        return cls
    enum_cls = _generate_enum(cls)
    _error_code_model.set(enum_cls)
    return enum_cls


def get_error_code_model() -> Enum:
    return _error_code_model.get()


class BizError(Exception):
    # FIXME: schema & type
    def __init__(self, error_code: Union[str, ErrorCode], error_msg: str = ""):
        self.error_code = str(error_code)
        self.error_msg = error_msg


def business_exception_response(exc: BizError) -> JSONResponse:
    return JSONResponse(
        jsonable_encoder(
            {
                "success": False,
                "errorCode": exc.error_code,
                "errorMsg": exc.error_msg,
                "data": {},
            }
        ),
        status_code=status.HTTP_200_OK,
    )


def register_business_exception_handler(app: FastAPI):
    @app.exception_handler(BizError)
    async def business_exception_handler(
        request: Request, exc: BizError
    ) -> JSONResponse:
        return business_exception_response(exc)
