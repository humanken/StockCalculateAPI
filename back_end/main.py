import uvicorn
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from back_end import api_status, engine, Base, DBContextManager
from back_end.api import (
    category_router, stock_router, dividend_router, calculate_router, session_router, other_router
)
from back_end.crawler import CategoryCrawler, StockCrawler, StockPriceCrawler, DividendCrawler
from back_end.crud import get_category_by_pid, get_stock_by_pid, get_dividend_by_pid
from back_end.scheduler import scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://127.0.0.1:8001',
        'http://localhost:8317',
        'http://192.168.3.117:8317',
        'http://192.168.6.76:8317',
        'https://calculate.hotpeperken.com'
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key='humanken-0317')

ROUTER_PREFIX = "/api/v0"
app.include_router(category_router, prefix=ROUTER_PREFIX)
app.include_router(stock_router, prefix=ROUTER_PREFIX)
app.include_router(dividend_router, prefix=ROUTER_PREFIX)
app.include_router(calculate_router, prefix=ROUTER_PREFIX)
app.include_router(session_router, prefix=ROUTER_PREFIX)
app.include_router(other_router, prefix=ROUTER_PREFIX)


@app.on_event("startup")
def startup():
    print('啟動定時任務...')
    scheduler.start()

    with DBContextManager() as db:
        # 判斷資料庫有沒有類別資料
        if not get_category_by_pid(db=db, pid=1):
            print('抓取【 股票類別 】並儲存到資料庫...')
            CategoryCrawler.start_and_save_to_db()

        time.sleep(2)

        # 判斷資料庫有沒有股票資料
        if not get_stock_by_pid(db=db, pid=1):
            print('抓取【 股票資訊 】並儲存到資料庫...')
            StockCrawler.start_and_save_to_db()
        else:
            print('更新現價資料...')
            StockPriceCrawler.start_and_update_with_db()

        time.sleep(2)

        # 判斷資料庫有沒有股利資料
        if not get_dividend_by_pid(db=db, pid=1):
            print('抓取【 股利資料 】並儲存到資料庫...')
            DividendCrawler.start_and_save_to_db()
        else:
            print('更新股利資料...')
            DividendCrawler.update_with_db()

        time.sleep(1)

        print('啟動股票試算...')
        api_status.set(True)
    return


@app.on_event('shutdown')
def shutdown():
    print('清除定時任務...')
    scheduler.remove_all_jobs()
    print('關閉定時任務...')
    scheduler.shutdown()
    print('關閉股票試算...')
    api_status.set(False)
    return


# if __name__ == "__main__":
#     uvicorn.run(app="app", host="0.0.0.0", port=8000)

