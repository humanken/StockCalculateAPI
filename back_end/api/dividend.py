# back_end/api/dividend.py

from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from back_end import get_db, api_status
from back_end.crud import dividend as crud
from back_end.schema import dividend as schema

router = APIRouter()

""" -------------------------------------- GET -------------------------------------- """
@router.get("/dividend/stock_year", response_model=schema.Read, tags=["單筆股利操作"], summary="透過 股票主鍵 和 年份 取得")
def read_dividend_by_stock_year(stock_id: int, year: str, db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API，請稍後再試")
    db_dividend = crud.get_dividend_by_stock_id_year(db=db, stock_id=stock_id, year=year)
    if db_dividend is None:
        raise HTTPException(status_code=404, detail=f"Dividend stock id: {stock_id}, year: {year} not found")
    return db_dividend


@router.get("/dividends", response_model=list[schema.Read], tags=["多筆股利操作"], summary="透過 股票主鍵 取得")
def read_dividends_by_stock(stock_id: int, limit: int = 10, db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API，請稍後再試")
    db_dividends = crud.get_dividends_by_stock(db=db, stock_id=stock_id, limit=limit)
    return db_dividends


@router.get("/dividend/update", response_class=JSONResponse, tags=["其他"])
def read_new_update(db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API，請稍後再試")
    return {'date': crud.get_latest_update_time(db=db).strftime('%Y/%m/%d')}


""" ------------------------------------- POST -------------------------------------- """


@router.post("/dividends", response_model=list[schema.Create], tags=["多筆股利操作"], summary="新增股利")
def create_dividends(dividends_create: list[schema.Create], db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API，請稍後再試")

    return crud.create_dividends(db=db, dividends_create=dividends_create)


""" ------------------------------------- PATCH ------------------------------------- """


@router.put("/dividends", response_model=list[schema.Update], tags=["多筆股利操作"], summary="更新 現金和股票 股利")
def update_dividends(dividends_update: list[schema.Update], db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API，請稍後再試")

    return crud.update_dividends(db=db, dividends_update=dividends_update)


""" ------------------------------------- DELETE ------------------------------------- """





