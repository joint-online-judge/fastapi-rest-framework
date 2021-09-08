from functools import lru_cache
from typing import Any, Generic, List, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, create_model

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
            error_code=(get_error_code_model(), ...),
            error_msg=(Optional[str], ...),
            data=data_type,
        ),
        sub_model,
    )


class Empty(BaseModel):
    pass


class StandardResponse(Generic[BT]):
    def __class_getitem__(cls, item: Any) -> Type[Any]:
        return get_standard_response_model(item)[0]

    def __new__(
        cls, data: Union[BT, Type[BT], Empty] = Empty()
    ) -> "StandardResponse[BT]":
        response_type, _ = get_standard_response_model(type(data))  # type: ignore
        response_data = data

        return response_type(  # type: ignore
            error_code=ErrorCode.Success, error_msg=None, data=response_data
        )


class StandardListResponse(Generic[BT]):
    def __class_getitem__(cls, item: Any) -> Type[Any]:
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
            error_code=ErrorCode.Success, error_msg=None, data=response_data
        )
