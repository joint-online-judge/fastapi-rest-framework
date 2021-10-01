from functools import lru_cache, wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, Generic, List, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, create_model
from pydantic.main import BaseConfig

from fastapi_rest_framework.errors import ErrorCode, get_error_code_model

BT = TypeVar("BT", bound=BaseModel)


@lru_cache(maxsize=None)
def get_standard_list_response_sub_model(
    cls: Type[BaseModel],
) -> Type[BaseModel]:
    name = cls.__name__
    return create_model(
        f"{name}List",
        count=(int, 0),
        results=(List[cls], []),  # type: ignore
    )


def snake_to_camel_case(string):
    return "".join(
        word.capitalize() if i else word for i, word in enumerate(string.split("_"))
    )


class Config(BaseConfig):
    alias_generator = snake_to_camel_case


@lru_cache(maxsize=None)
def get_standard_response_model(
    cls: Type[BaseModel], is_list: bool = False
) -> Tuple[Type[BaseModel], Optional[Type[BaseModel]]]:
    name = cls.__name__
    sub_model: Optional[Type[BaseModel]]
    if is_list:
        model_name = f"{name}ListResp"
        sub_model = get_standard_list_response_sub_model(cls)
        data_type = (Optional[sub_model], None)
    else:
        model_name = f"{name}Resp"
        sub_model = None
        data_type = (Optional[cls], None)
    return (
        create_model(
            model_name,
            success=(bool, ...),
            error_code=(get_error_code_model(), ...),
            error_msg=(Optional[str], ...),
            data=data_type,
            __config__=Config,
        ),
        sub_model,
    )


class Empty(BaseModel):
    pass


class StandardResponse(Generic[BT]):
    def __class_getitem__(cls, item: Any) -> Type[Any]:
        if item is None or item == Any:
            item = Empty
        return get_standard_response_model(item)[0]

    def __new__(
        cls, data: Union[BT, Type[BT], Empty] = Empty()
    ) -> "StandardResponse[BT]":
        if data is None:
            data = Empty()
        response_type, _ = get_standard_response_model(type(data))  # type: ignore
        response_data = data

        return response_type(  # type: ignore
            success=True,
            errorCode=ErrorCode.Success,
            errorMsg=None,
            data=response_data,
        )


class StandardListResponse(Generic[BT]):
    def __class_getitem__(cls, item: Any) -> Type[Any]:
        if item is None or item == Any:
            item = Empty
        return get_standard_response_model(item, True)[0]

    def __new__(
        cls,
        results: Optional[List[Union[BT, Type[BT], Empty]]] = None,
        count: Optional[int] = None,
    ) -> "StandardListResponse[BT]":
        if results is None:
            results = []
        data_type = len(results) and type(results[0]) or Empty
        response_type, sub_model_type = get_standard_response_model(
            data_type, True  # type: ignore
        )
        if count is None:
            count = len(results)
        response_data: BaseModel
        if sub_model_type is None:
            response_data = Empty()
        else:
            response_data = sub_model_type(count=count, results=results)

        return response_type(  # type: ignore
            success=True,
            errorCode=ErrorCode.Success,
            errorMsg=None,
            data=response_data,
        )


def standard_response(func: Callable[..., Any]) -> Callable[..., Any]:
    func.__annotations__["return"] = StandardResponse[func.__annotations__["return"]]  # type: ignore
    if iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> StandardResponse[Any]:
            return StandardResponse(await func(*args, **kwargs))

    else:

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> StandardResponse[Any]:
            return StandardResponse(func(*args, **kwargs))

    return wrapper


def standard_list_response(func: Callable[..., Any]) -> Callable[..., Any]:
    anno = func.__annotations__
    if anno["return"].__origin__ == tuple:
        anno["return"] = anno["return"].__args__[0].__args__[0]
    anno["return"] = StandardListResponse[anno["return"]]  # type: ignore
    if iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> StandardListResponse[Any]:
            res = await func(*args, **kwargs)
            if not isinstance(res, list):
                return StandardListResponse(res[0], res[1])
            return StandardListResponse(res)

    else:

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> StandardListResponse[Any]:
            res = func(*args, **kwargs)
            if not isinstance(res, list):
                return StandardListResponse(res[0], res[1])
            return StandardListResponse(res)

    return wrapper
