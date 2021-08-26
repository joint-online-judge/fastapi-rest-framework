from typing import TYPE_CHECKING, Any, Callable, get_type_hints

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import StreamingResponse


class Detail(BaseModel):
    detail: str


class Router(APIRouter):
    """
    Overrides the route decorator logic to use the annotated return type as the `response_model` if unspecified.
    Modified from fastapi_utils.inferring_router
    """

    if not TYPE_CHECKING:  # pragma: no branch

        def add_api_route(
            self, path: str, endpoint: Callable[..., Any], **kwargs: Any
        ) -> None:
            if kwargs.get("response_model") is None:
                res = get_type_hints(endpoint).get("return")
                if res != StreamingResponse:
                    kwargs["response_model"] = res
            kwargs["responses"] = {403: {"model": Detail}}
            return super().add_api_route(path, endpoint, **kwargs)
