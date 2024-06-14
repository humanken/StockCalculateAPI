# back_end/api/calculate.py

import json
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from back_end import get_db, api_status, Calculate
from back_end.schema import calculate as schema
from back_end.crud.stock import get_stocks

router = APIRouter()

""" -------------------------------------- POST -------------------------------------- """
@router.post("/calculates", tags=["試算資料操作"], summary="透過 股票代號 計算取得")
def read_calculates_by_stocks(params: schema.Get, db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")

    # 建立 schema model
    model = schema.create_dynamic_model(yield_start=params.yieldStart, yield_end=params.yieldEnd)

    result = Calculate(
        db=db, model=model,
        stock_numbers=params.numbers,
        yield_start=params.yieldStart,
        yield_end=params.yieldEnd
    ).result
    return result


@router.post("/calculatesQuery", tags=["試算資料操作"], summary="透過 類別篩選取得股票物件 計算取得")
def read_calculates_by_query_stocks(query: schema.QueryGet, db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")

    # 建立 schema model
    model = schema.create_dynamic_model(yield_start=query.yieldStart, yield_end=query.yieldEnd)

    stocks, all_length = get_stocks(db=db, skip=query.skip, limit=query.limit, excludes=query.excludes)

    result = Calculate(
        db=db, model=model,
        stocks=stocks,
        yield_start=query.yieldStart,
        yield_end=query.yieldEnd
    ).result

    return schema.QueryResponse(**{
        'nextOffset': skip if (skip := (query.skip + query.limit)) <= all_length else None,
        'limit': query.limit,
        'length': all_length,
        'data': result
    })
