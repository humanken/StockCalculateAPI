# back_end/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from back_end import api_status, engine
from back_end.crawler import StockPriceCrawler, DividendCrawler

scheduler_init = {
    # 配置儲存
    'jobstores': {'default': SQLAlchemyJobStore(engine=engine)},
    # 配置線程
    'executors': {'default': ThreadPoolExecutor(6)},
    # 創建job默認參數
    'job_defaults': {
        'coalesce': False,   # 是否合併執行
        'max_instances': 1  # 最大執行實例數
    }
}
scheduler = BackgroundScheduler(**scheduler_init)


def stop_api():
    print('API 暫停，準備更新')
    api_status.set(False)
    return

def start_api():
    print('更新完畢，啟動 API')
    api_status.set(True)
    return

# 更新昨日收盤價 (每日 00:06 執行)
def update_price():
    # 如果api啟動中，則暫停api
    if api_status.is_running:
        api_status.set(False)
    print('Update Price, Every Day Update')
    StockPriceCrawler.start_and_update_with_db()
    print('Update Price Finished')


# 更新股利 (每週ㄧ 00:01 執行)
def update_dividend():
    # 如果api啟動中，則暫停api
    if api_status.is_running:
        api_status.set(False)
    print('Update Dividend, Every Week Update')
    DividendCrawler.update_with_db()
    print('Update Dividend Finished')


# 00:00 關閉api，準備更新
scheduler.add_job(stop_api, 'cron', **{'hour': 0, 'minute': 0})

# 每週一 00:10 更新股利
scheduler.add_job(update_dividend, 'cron', **{'day_of_week': 0, 'hour': 0, 'minute': 10})

# 00:20 更新收盤價
scheduler.add_job(update_price, 'cron', **{'hour': 0, 'minute': 20})

# 00:30 更新完畢，啟動api
scheduler.add_job(start_api, 'cron', **{'hour': 0, 'minute': 30})



