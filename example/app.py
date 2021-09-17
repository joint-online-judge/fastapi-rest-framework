from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger

from example.config import FastAPIConfig
from fastapi_rest_framework import config, logging

logging.init_logging()
logging.intercept_all_loggers()
config.init_settings(FastAPIConfig)
app = FastAPI()
app.logger = logger


# @errors.register_error_code_model
# class ErrorCode(errors.ErrorCode):
#     UserError = "UserError"


@app.get("/")
async def redirect_to_docs() -> RedirectResponse:
    app.logger.info("")
    return RedirectResponse(url="/docs?docExpansion=none")
