from typing import List, Tuple

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from example.config import FastAPIConfig
from fastapi_rest_framework import config, logging
from fastapi_rest_framework.errors import (
    BizError,
    ErrorCode as BaseErrorCode,
    register_business_exception_handler,
)
from fastapi_rest_framework.responses import (
    Empty,
    standard_list_response,
    standard_response,
)

logging.init_logging()
logging.intercept_all_loggers()
config.init_settings(FastAPIConfig)
app = FastAPI()


# @register_error_code_model
class ErrorCode(BaseErrorCode):
    UserError = "UserError"


register_business_exception_handler(app)


@app.get("/")
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs?docExpansion=none")


@app.get("/aempty")
@standard_response
async def async_empty() -> None:
    return


@app.get("/empty")
@standard_response
async def sync_empty() -> None:
    return


@app.get("/aemptys")
@standard_list_response
async def async_empty_list() -> List[Empty]:
    return []


@app.get("/emptys")
@standard_list_response
async def sync_empty_list() -> List[Empty]:
    return []


@app.get("/aemptys/count")
@standard_list_response
async def async_empty_list_count() -> Tuple[List[Empty], int]:
    return [], 5


@app.get("/emptys/count")
@standard_list_response
async def sync_empty_list_count() -> Tuple[List[Empty], int]:
    return [], 5


@app.get("/bizerror")
@standard_response
async def bizerror() -> None:
    # FIXME: schema & type
    raise BizError(ErrorCode.NotFoundError)  # type: ignore
