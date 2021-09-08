from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger

from fastapi_rest_framework import errors, logging

logging.init_logging()
app = FastAPI()
app.logger = logger


@errors.register_error_code_model
class ErrorCode(errors.ErrorCode):
    UserError = "UserError"


@app.get("/")
async def redirect_to_docs() -> RedirectResponse:
    app.logger.info("")
    return RedirectResponse(url="/docs?docExpansion=none")
