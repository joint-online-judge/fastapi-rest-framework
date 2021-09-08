from functools import wraps
from inspect import Parameter, Signature
from typing import Any, Callable, List, Optional

from fastapi import Query
from makefun import with_signature
from pydantic import NonNegativeInt, conint

from fastapi_rest_framework.errors import BizError, ErrorCode
from fastapi_rest_framework.schemas import FilterQuery, OrderingQuery, PaginationQuery


def parse_pagination_query(
    max_limit: Optional[NonNegativeInt] = 500, default_limit: NonNegativeInt = 10
) -> Callable[..., PaginationQuery]:
    LimitType = conint(ge=0, le=max_limit)

    @wraps
    def wrapped(
        offset: NonNegativeInt = Query(0),
        limit: LimitType = Query(default_limit),  # type: ignore
    ) -> PaginationQuery:
        return PaginationQuery(offset=offset, limit=NonNegativeInt(limit))

    return wrapped


def parse_ordering_query(
    fields: Optional[List[str]] = None,
) -> Callable[..., OrderingQuery]:
    if fields is not None:
        fields_set = set(fields)

    @wraps
    def wrapped(
        ordering: str = Query(
            "",
            description="Comma seperated list of ordering the results.\n"
            "You may also specify reverse orderings by prefixing the field name with '-'.",
            example="-updated_at",
        ),
    ) -> OrderingQuery:
        orderings = list(filter(None, ordering.split(",")))
        if fields is not None:
            for x in orderings:
                name = x.startswith("-") and x[1:] or x
                if name not in fields_set:
                    raise BizError(
                        ErrorCode.IllegalFieldError,
                        f"{x} is not available in ordering fields",
                    )
        return OrderingQuery(orderings=orderings)

    return wrapped


def parse_filter_query(
    fields: Optional[List[str]] = None,
) -> Callable[..., FilterQuery]:
    if fields is None:
        fields = []
    parameters = [
        Parameter(
            name=field,
            kind=Parameter.KEYWORD_ONLY,
            annotation=str,
            default=Query("", description=f"F{field} filter"),
        )
        for field in fields
    ]
    signature = Signature(parameters)

    @with_signature(signature)
    def wrapped(**kwargs: Any) -> FilterQuery:
        return FilterQuery(fields=kwargs)

    return wrapped
