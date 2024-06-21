# back_end/crawler/dividend.py
import os
import time, random
from datetime import datetime
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from back_end import DBContextManager, timer
from back_end.schema.dividend import Create, Update
from back_end.crud import (
    get_stock_by_number,
    create_dividends, update_dividends,
    is_dividend_of_year_exist
)


class DividendCrawler:
    def __init__(self):
        self.GoodInfoUrl = 'https://goodinfo.tw/tw/StockDividendPolicyList.asp'

    @staticmethod
    def _setup_driver() -> WebDriver:
        options = webdriver.ChromeOptions()
        # 關閉 'chrome正在自動化' 提示
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # 不顯示視窗模式
        options.add_argument("--headless")
        # 設置請求標頭
        options.add_argument("user-agent=%s" % UserAgent().random)

        # use driver when local
        driver = webdriver.Chrome(
            service=Service(executable_path=ChromeDriverManager().install()),
            options=options
        )
        # use driver when deploy docker compose
        # driver = webdriver.Remote(
        #     command_executor='http://selenium:4444/wd/hub',
        #     options=options
        # )
        return driver

    @staticmethod
    def _params_transform_url(year: int):
        params = {
            'MARKET_CAT': '全部',
            'INDUSTRY_CAT': '全部'
        }
        url = '?'
        for key, val in params.items():
            url += f'{key}={val}&'
        url += f'YEAR={year}'
        return url

    def _get_all_by_year(self, year: int):
        driver = self._setup_driver()
        driver.get(self.GoodInfoUrl + self._params_transform_url(year=year))

        number_data = []
        dividend_data = {}
        try:
            print('等待網頁加載...')
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "tblDetail"))
            )
            bsp = BeautifulSoup(driver.page_source, 'html.parser')
            tr_elements = bsp.find('table', id="tblDetail").findChildren('tr', align="center")

            for row in tr_elements:
                cols = row.findChildren('td')
                number = cols[1].text
                cash = round(float(cols[9].text), 3)
                stock = round(float(cols[12].text), 3)
                number_data.append(number)
                dividend_data[number] = [cash, stock]
        except Exception as e:
            print(e)
        finally:
            driver.quit()
        return number_data, dividend_data

    @classmethod
    @timer
    def update_with_db(cls):
        cls_ = cls()
        year = datetime.now().year
        numbers, dividends = cls_._get_all_by_year(year=year)

        mix_data = {'create': [], 'update': {'instances': [], 'data': []}}
        with DBContextManager() as db:
            for number in numbers:
                # 判斷 資料庫是否存在此股票obj
                if (stock_obj := get_stock_by_number(db=db, number=number)) is None:
                    continue
                data = {
                    'year': str(year), 'stock_id': stock_obj.id,
                    'cash': dividends[number][0], 'stock': dividends[number][1]
                }
                # 判斷 資料庫是否存在同年份的股利
                # 不存在   -> 新增股利
                # 存在    -> 更新股利
                if (dividend_obj := is_dividend_of_year_exist(
                        stock_obj.dividends, year=str(year)
                )) is False:
                    mix_data['create'].append(Create(**data))
                else:
                    mix_data['update']['instances'].append(dividend_obj)
                    mix_data['update']['data'].append(Update(**data))

            create_dividends(db=db, dividends_create=mix_data['create'])
            update_dividends(
                db=db,
                instances=mix_data['update']['instances'],
                dividends_update=mix_data['update']['data']
            )
        return

    @classmethod
    @timer
    def start_and_save_to_db(cls):
        cls_ = cls()
        year = datetime.now().year
        with DBContextManager() as db:
            for y in range(0, 10):
                numbers, dividends = cls_._get_all_by_year(year=(year - y))

                dividends_create = []
                for number in numbers:
                    # 判斷 資料庫是否存在此股票obj
                    if (stock_obj := get_stock_by_number(db=db, number=number)) is None:
                        continue
                    data = {
                        'year': str(year - y), 'stock_id': stock_obj.id,
                        'cash': dividends[number][0], 'stock': dividends[number][1]
                    }
                    # 判斷 資料庫是否存在同年份的股利
                    # 不存在   -> 新增股利
                    if is_dividend_of_year_exist(stock_obj.dividends, year=str(year - y)) is False:
                        dividends_create.append(Create(**data))
                create_dividends(db=db, dividends_create=dividends_create)

                time.sleep(delay := random.randint(20, 30))
                print(f'catch year: {year - y} finished, delay: {delay}s')
        return


# if __name__ == "__main__":
    # DividendCrawler()._get_all_by_year(2024)

