# back_end/schema/calculate.py

from typing import Union
from pydantic import BaseModel, create_model


class CalculateBase(BaseModel):
    averageCashDividend: float
    averageStockDividend: float
    averageDividend: str
    averageYield: Union[str, None] = None
    roi: Union[str, None] = None


class Read(CalculateBase):
    stockName: str
    stockNumber: str
    stockFullName: str
    stockPrice: Union[float, None]
    stockDividendURL: str

    yieldStart: int
    yieldEnd: int


class Get(BaseModel):
    numbers: list[str]
    yieldStart: int = 2
    yieldEnd: int = 8


class QueryGet(BaseModel):
    skip: int = 0
    limit: int = 50
    excludes: Union[list[int], None]
    yieldStart: int = 2
    yieldEnd: int = 8


class QueryResponse(BaseModel):
    nextOffset: Union[int, None] = 0
    limit: int
    length: int
    data: list


def create_dynamic_model(yield_start: int, yield_end: int):
    fields = {
        key: (t, ...)
        for cls in [CalculateBase, Read]
        for key, t in cls.__annotations__.items()
    }
    for i in range(yield_start, yield_end + 1):
        fields[f'yield{i}ConvertPrice'] = (float, ...)
    return create_model('YieldConvertPriceModel', **fields)
