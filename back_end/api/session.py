# back_end/api/session.py

from fastapi import Request, HTTPException, APIRouter, Response
from fastapi.responses import JSONResponse
import requests
from back_end import api_status


router = APIRouter()


@router.get('/session')
async def get_session(request: Request):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")

    print(f'request: {request}, get excludes: {request.session}')
    return {'excludes': request.cookies.get('session', {}).get('excludes', [])}


@router.post('/session')
async def set_session(request: Request, response: Response):
    if not api_status.is_running:
        raise HTTPException(status_code=404, detail="系統更新中已關閉API服務，請稍後再試")
    param = await request.json()
    if (data := param.get('session', None)) is None:
        raise HTTPException(status_code=500, detail="參數錯誤")
    response.set_cookie(key='session', value=data)
    print(f'request: {request}, set excludes: {request.session}')
    return JSONResponse(status_code=200, content={"msg": "success"})



