# back_end/schema/category.py

from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    type: str
    sector_id: int


class Create(CategoryBase):
    pass


class Read(CategoryBase):
    id: int

    class Config:
        from_attribute = True




