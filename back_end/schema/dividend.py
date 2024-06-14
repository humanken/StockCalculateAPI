# back_end/schema/dividend.py

from pydantic import BaseModel


class DividendBase(BaseModel):
    year: str
    cash: float
    stock: float


class Update(DividendBase):
    stock_id: int


class Create(Update):
    pass


class Delete(Update):
    pass


class Read(DividendBase):
    id: int

    class Config:
        # orm_mode = True
        from_attributes = True



