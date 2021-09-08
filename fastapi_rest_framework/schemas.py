from typing import Dict, List

from pydantic import BaseModel, ConstrainedStr, NonNegativeInt, PositiveInt

# class NoneNegativeInt(ConstrainedInt):
#     ge = 0
#
#
# class PositiveInt(ConstrainedInt):
#     gt = 0


class PaginationLimit(PositiveInt):
    le = 500


class LongStr(ConstrainedStr):
    max_length = 255


class NoneEmptyStr(ConstrainedStr):
    min_length = 1


class NoneEmptyLongStr(LongStr, NoneEmptyStr):
    pass


class OrderingQuery(BaseModel):
    orderings: List[str]


class PaginationQuery(BaseModel):
    offset: NonNegativeInt
    limit: NonNegativeInt


class FilterQuery(BaseModel):
    fields: Dict[str, str]
