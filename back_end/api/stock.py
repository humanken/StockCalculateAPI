# back_end/api/stock.py

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from back_end import get_db, api_status
from back_end.crud import stock as crud
from back_end.schema import stock as schema

router = APIRouter()

""" -------------------------------------- GET -------------------------------------- """

@router.get("/stock/pid/{pid}", response_model=schema.Read, tags=["單筆股票操作"], summary="透過 主鍵 取得")
def read_stock_by_id(pid: int, db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")
    db_stock = crud.get_stock_by_pid(db=db, pid=pid)
    if db_stock is None:
        raise HTTPException(status_code=500, detail=f"Stock pid: {pid} not found")
    return db_stock


@router.get("/stock/detail/number/{number}", response_model=schema.ReadDetail, tags=["具有詳細資料的股票操作"], summary="透過 代碼 取得")
@router.get("/stock/number/{number}", response_model=schema.Read, tags=["單筆股票操作"], summary="透過 代碼 取得")
def read_stock_by_number(number: str, db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")
    db_stock = crud.get_stock_by_number(db=db, number=number)
    if db_stock is None:
        raise HTTPException(status_code=500, detail=f"Stock number: {number} not found")
    return db_stock


@router.get("/stocks", response_model=list[schema.Read], tags=["多筆股票操作"], summary="預設一次取得1000筆資料")
def read_stocks(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")
    db_stock, _ = crud.get_stocks(db=db, skip=skip, limit=limit)
    return db_stock

""" ------------------------------------- POST -------------------------------------- """

@router.post("/stocks/", response_model=list[schema.Create], tags=["多筆股票操作"], summary="新增股票")
def create_stock(stocks_create: list[schema.Create], db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")

    return crud.create_stocks(db=db, stocks_create=stocks_create)


""" ------------------------------------- PATCH ------------------------------------- """


@router.patch("/stocks/", response_model=list[schema.Update], tags=["多筆股票操作"], summary="更新現價")
def update_prices(stocks_update: list[schema.Update], db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")

    return crud.update_prices(db=db, stocks_update=stocks_update)


""" ------------------------------------- DELETE ------------------------------------- """


