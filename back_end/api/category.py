# back_end/api/category.py

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from back_end import get_db, api_status
from back_end.crud import category as crud
from back_end.schema import category as schema

router = APIRouter()

""" -------------------------------------- GET -------------------------------------- """

@router.get("/categories", response_model=list[schema.Read], tags=["多筆類別操作"], summary="上市/上櫃 類別可選")
def read_categories(twse: bool = True, otc: bool = True, db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")
    if not twse and not otc:
        raise HTTPException(status_code=500, detail="Parameters(twse/otc) only one False")

    db_cat = []
    if twse:
        db_cat.extend(crud.get_categories_of_twse(db=db))
    if otc:
        db_cat.extend(crud.get_categories_of_otc(db=db))
    return db_cat


""" ------------------------------------- POST -------------------------------------- """

@router.post("/category", response_model=schema.Create, tags=["單筆類別操作"], summary="新增類別")
def create_category(cat_create: schema.Create, db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")

    return crud.create_category(db=db, cat_create=cat_create)


@router.post("/categories", response_model=list[schema.Create], tags=["多筆類別操作"], summary="新增類別")
def create_categories(cats_create: list[schema.Create], db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")
    try:
        db_cats = crud.create_categories(db=db, cats_create=cats_create)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return db_cats


""" ------------------------------------- PATCH ------------------------------------- """

""" ------------------------------------- DELETE ------------------------------------- """


