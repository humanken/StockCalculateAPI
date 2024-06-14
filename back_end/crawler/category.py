# back_end/crawler/category.py

import re
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from bs4.element import Tag
from back_end import DBContextManager, timer
from back_end.schema.category import Create
from back_end.crud import create_categories


class CategoryCrawler:
    def __init__(self):
        self.YahooCategoryURL = "https://tw.stock.yahoo.com/class"
        self.TypeIDs = {
            'twse': "LISTED_STOCK",
            'otc': "OVER_THE_COUNTER_STOCK"
        }
        self.CreateDataFormat = {'name': '', 'type': '', 'sector_id': ''}
        self.Excludes = ["市認購", "市認售", "市牛證", "市熊證", "指數類", "櫃公司債", "櫃認購", "櫃認售", "櫃指數類"]

    def _get_html_response(self) -> BeautifulSoup:
        headers = {'user-agent': UserAgent().random}
        resp = requests.get(self.YahooCategoryURL, headers=headers)
        return BeautifulSoup(resp.text, 'html.parser')

    @staticmethod
    def _response_filter_type(resp: BeautifulSoup, type_id: str) -> list[Tag]:
        return [a for a in resp.find('div', id=type_id).find('ul').find_all('a', href=True)]

    def _get_create_data_from_resp(self, resp: Tag, type: str):
        if (name := resp.string) in self.Excludes:
            return None
        self.CreateDataFormat = {
            'name': name,
            'type': type,
            'sector_id': re.search(r'sectorId=(.*)&exchange=(.*)', str(resp.attrs['href']), re.I).group(1)
        }
        return Create(**self.CreateDataFormat)

    @classmethod
    @timer
    def start_and_save_to_db(cls):
        cls_ = cls()
        response = cls_._get_html_response()
        create_data = [
            data
            for key, value in cls_.TypeIDs.items()
            for resp_filter in cls_._response_filter_type(resp=response, type_id=value)
            if (data := cls_._get_create_data_from_resp(resp=resp_filter, type=key)) is not None
        ]
        with DBContextManager() as db:
            create_categories(db=db, cats_create=create_data)
        return


# if __name__ == '__main__':
#     CategoryCrawler.start_and_save_to_db()

