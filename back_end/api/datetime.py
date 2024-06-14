from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from back_end import get_db, api_status
from back_end.crud import stock as stock_crud
from back_end.crud import dividend as dividend_crud

router = APIRouter()


@router.get("/updateTime", response_class=JSONResponse, tags=["其他"])
def read_new_update(db: Session = Depends(get_db)):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")
    datetimeformat = '%Y-%m-%dT%H:%M:%S'
    price_update = stock_crud.get_latest_update_time(db=db).strftime('%H:%M:%S')
    dividend_update = dividend_crud.get_latest_update_time(db=db).strftime('%Y-%m-%d')
    return {'price': price_update, 'dividend': dividend_update, 'format': datetimeformat}
