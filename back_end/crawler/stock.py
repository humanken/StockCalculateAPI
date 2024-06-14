# back_end/crawler/stock.py

import random
import time
import requests
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from back_end import DBContextManager, timer
from back_end.schema.stock import Create, Update
from back_end.crud import (
    create_stocks,
    get_categories_of_otc, get_categories_of_twse,
    update_prices
)


class StockCrawler:
    def __init__(self):
        # self.TwseByCatYahooURL = "https://tw.stock.yahoo.com/class/class-quote?sectorId={}&exchange=TAI"
        # self.OtcByCatYahooURL = "https://tw.stock.yahoo.com/class/class-quote?sectorId={}&exchange=TWO"
        # self.URLParameters = {'offset': 0, 'exchange': 'TAI', 'sectorId': 1}
        # self.YahooApiUrl = "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuoteHolders;"
        self.YahooApiUrl = "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;"

    def _get_response_data(self, offset=0, sector_id=1, exchange='TAI'):
        headers = {'user-agent': UserAgent().random}
        return requests.get(
            self._add_params_in_url(offset=offset, sector_id=sector_id, exchange=exchange),
            headers=headers
        ).json()

    def _add_params_in_url(self, offset=0, exchange='TAI', sector_id=1):
        return f"{self.YahooApiUrl}offset={offset};exchange={exchange};sectorId={sector_id}"

    @staticmethod
    def _convert_to_create_data(cat_pid: int, stock_data: dict) -> Create or None:
        try:
            data = {
                'cat_id': cat_pid,
                'number': stock_data['systexId'],
                'name': stock_data['symbolName'],
                'price': float(price) if (price := stock_data['price']['sort']) else None
            }
            return Create(**data)
        except Exception as e:
            print(f"category id: {cat_pid}, stock: {stock_data['systexId']} convert error: {e}")
            return None

    def _get_data_by_category(self, cat_obj, exchange='TAI') -> list[Create]:
        next_offset = 0
        create_data = []
        # 每次請求，只能取得30筆資料
        while True:
            resp = self._get_response_data(
                offset=next_offset, sector_id=cat_obj.sector_id, exchange=exchange
            )
            if (data := resp['list']) is None:
                raise ValueError('Send request, but response no data')

            create_data.extend(
                [self._convert_to_create_data(cat_pid=cat_obj.id, stock_data=d)
                 for d in data if d]
            )
            # 間斷，避免被擋
            time.sleep(random.randint(1, 5))

            # 當nextOffset為None，代表沒有資料，不需再發request
            if (next_offset := resp['pagination']['nextOffset']) is None:
                break
        return create_data

    @classmethod
    @timer
    def start_and_save_to_db(cls):
        cls_ = cls()
        with DBContextManager() as db:
            # twse ----------------------------------------------------------------------
            for cat_obj in get_categories_of_twse(db=db):
                create_data = cls_._get_data_by_category(cat_obj=cat_obj, exchange='TAI')
                create_stocks(db=db, stocks_create=create_data)
                time.sleep(random.randint(1, 5))

            # otc ----------------------------------------------------------------------
            for cat_obj in get_categories_of_otc(db=db):
                create_data = cls_._get_data_by_category(cat_obj=cat_obj, exchange='TWO')
                create_stocks(db=db, stocks_create=create_data)
                time.sleep(random.randint(1, 5))
        return


class StockSourceType:
    def __init__(self, source_type):
        if source_type not in ['twse', 'otc']:
            raise ValueError("StockSourceType Param: source_type only 'twse' or 'otc'")
        self._Type = source_type

        self._TwseURL = 'https://www.twse.com.tw/exchangeReport/MI_INDEX'
        self._OtcURL = 'https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php'
        self._URLsAndParams = {
            'twse': {'url': self._TwseURL, 'param': {'response': 'json', 'type': 'ALL'}},
            'otc': {'url': self._OtcURL, 'param': {'l': 'zh-tw', 'se': 'AL'}}
        }

        self._KeysDataAndPriceIndex = {
            'twse': {'d': 'data9', 'i': 8},
            'otc': {'d': 'aaData', 'i': 2}
        }

    @property
    def url(self):
        return self._URLsAndParams[self._Type]['url']

    @property
    def param(self):
        return self._URLsAndParams[self._Type]['param']

    @property
    def data_key(self):
        return self._KeysDataAndPriceIndex[self._Type]['d']

    @property
    def price_index(self):
        return self._KeysDataAndPriceIndex[self._Type]['i']

class StockPriceCrawler:
    def __init__(self):
        self.MisTwseURL = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp'
        self.SourceTypes = ['twse', 'otc']

    @staticmethod
    def _get_response_data(source_type):
        source = StockSourceType(source_type=source_type)
        headers = {'user-agent': UserAgent().random}
        try:
            resp_json = requests.get(
                url=source.url, params=source.param, headers=headers
            ).json()

            if 'stat' in list(resp_json.keys()):
                if resp_json['stat'] != "OK":
                    raise ValueError('Send request, but response no TWSE price data')
            elif 'aaData' not in list(resp_json.keys()):
                raise ValueError('Send request, but response no OTC price data')
            return resp_json
        except Exception as e:
            print(e)
        return

    @staticmethod
    def _convert_to_update_data(number: str, price: float or None):
        return Update(**{'number': number, 'price': price})

    @staticmethod
    def _handler_data_by_type(source_type, data) -> list[Update]:
        # twse: ["證券代號","證券名稱","成交股數","成交筆數","成交金額",
        # "開盤價","最高價","最低價","收盤價","漲跌(+/-)","漲跌價差",
        # "最後揭示買價","最後揭示買量","最後揭示賣價","最後揭示賣量","本益比"]
        source = StockSourceType(source_type=source_type)
        empties = ['--', '----']

        return [
            StockPriceCrawler._convert_to_update_data(
                number=d[0],
                price=float(price.replace(',', ''))
                if (price := str(d[source.price_index])) not in empties else None
            ) for d in data[source.data_key]
        ]

    @staticmethod
    def _update_with_db(db, update_data: list[Update]):
        return update_prices(db=db, stocks_update=update_data)

    @classmethod
    @timer
    def start_and_update_with_db(cls):
        with DBContextManager() as db:
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = {
                    executor.submit(cls._get_response_data, source_type): source_type
                    for source_type in cls().SourceTypes
                }

                for future in as_completed(futures):
                    data = cls._handler_data_by_type(
                        source_type=futures[future], data=future.result()
                    )
                    cls._update_with_db(db=db, update_data=data)
        return


# if __name__ == '__main__':
#     StockCrawler.start_and_save_to_db()




