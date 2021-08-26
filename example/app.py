from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger

from fastapi_rest_framework import logging

logging.init_logging()
app = FastAPI()
app.logger = logger


@app.get("/")
async def redirect_to_docs() -> RedirectResponse:
    app.logger.info("")
    return RedirectResponse(url="/docs?docExpansion=none")
