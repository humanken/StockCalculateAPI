# back_end/schema/stock.py

from typing import Union
from pydantic import BaseModel
from .category import CategoryBase
from .dividend import DividendBase


class StockBase(BaseModel):
    number: str
    name: str
    price: Union[float, None] = None


class Create(StockBase):
    cat_id: int
    pass


class Update(BaseModel):
    number: str
    price: Union[float, None] = None


class Read(StockBase):
    id: int
    category: CategoryBase

    class Config:
        # orm_mode = True
        from_attributes = True


class ReadDetail(Read):
    dividends: Union[list[DividendBase], None] = []
    # calculate
    pass


