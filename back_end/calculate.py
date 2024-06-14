# back_end/calculate.py

from sqlalchemy.orm import Session
from back_end import StockModel, DividendModel
from back_end.crud import get_stock_by_number

class Calculate:

    def __init__(
            self,
            db: Session,
            model,
            yield_start: int, yield_end: int,
            stock_numbers: list[str] = None, stocks: list[StockModel] = None
    ):
        self._DB = db
        self._Model = model

        self._StartYield = yield_start
        self._EndYield = yield_end

        if not stock_numbers and not stocks:
            raise ValueError("Calculate Params Error, params: stock_numbers/stocks must one have data")
        self._Stocks = stocks if stocks else self._get_stocks_by_numbers(numbers=stock_numbers)

        self._Yields = [(i / 100) for i in range(self._StartYield, self._EndYield + 1)]
        self._GoodInfoURL = 'https://goodinfo.tw/tw/StockDividendPolicy.asp?STOCK_ID={}'

        self._Results: list[model] = []

    def _get_stocks_by_numbers(self, numbers) -> list[StockModel]:
        return [get_stock_by_number(db=self._DB, number=n) for n in numbers]

    @staticmethod
    def _average_dividend(dividends: list[DividendModel]) -> tuple[float, float]:
        """
        計算 平均股利（現金、股票）

        :param dividends:
        :return: cash(float), stock(float)
        """
        d_length = float(len(dividends))
        if d_length == 0.0:
            return 0.0, 0.0
        cashes = []
        stocks = []
        for obj in dividends:
            cashes.append(obj.cash)
            stocks.append(obj.stock)
        return round(round(sum(cashes), 2)/d_length, 2), round(round(sum(stocks), 2)/d_length, 2)

    @staticmethod
    def _average_yield(v_cash: float, price: float or None) -> str or None:
        """
        以 目前價格 計算 殖利率
        formula: 殖利率(%) ＝ (平均現金股利 / 價格) ＊ 100
        :param v_cash: 平均現金股利
        :param price: 價格
        :return: str
        """
        if price is None:
            return None
        return '{:.2f}%'.format(round((v_cash / price) * 100, 2))

    @staticmethod
    def _return_on_investment(price: float or None, v_cash: float, v_stock: float) -> str or None:
        """
        投資報酬率 (ROI)，以一張(1000股)計算
        現金股利與股票股利(以目前現價計算股票股利) 轉為現金 ，除以成本(目前現價)
        :param price: 價格
        :param v_cash: 平均現金股利
        :param v_stock: 平均股票股利
        :return: ROI 百分比(%)
        """
        if price is None:
            return None
        # 計算 淨收入
        net_income = v_cash * 1000 + (v_stock / 10 * price) * 1000
        # 成本
        cost = price * 1000
        return "{:.2f}%".format(round((net_income / cost) * 100, 2))

    def _yields_convert_prices(self, v_cash: float) -> list[float]:
        """
        假設「各殖利率」以「平均現金股利」計算「價格」

        formula: 價格 ＝ 平均現金股利 / 殖利率

        :param v_cash: 平均現金股利
        :return: list[float]
        """
        if v_cash == 0.0:
            return [0.00 for _ in self._Yields]
        return [round(v_cash / percent, 2) for percent in self._Yields]

    def _convert_to_model_data(
            self, stock: StockModel,
            v_cash: float, v_stock: float, v_yield: str or None,
            roi: str or None, yields_convert_prices: list[float]):

        data = {
            'yieldStart': self._StartYield, 'yieldEnd': self._EndYield,
            'stockName': stock.name,
            'stockNumber': stock.number,
            'stockFullName': f'{stock.name}({stock.number})',
            'stockPrice': stock.price,
            'stockDividendURL': self._GoodInfoURL.format(stock.number),
            'averageCashDividend': v_cash, 'averageStockDividend': v_stock,
            'averageDividend': f'{v_cash}/{v_stock}',
            'averageYield': v_yield,
            'roi': roi
        }
        for i, price in enumerate(yields_convert_prices):
            data[f'yield{i + self._StartYield}ConvertPrice'] = price
        return self._Model(**data)

    def _calculate_result(self):
        """
        開始計算 並儲存在 _Results
        :return:
        """

        for stock in self._Stocks:
            try:
                v_cash_dividend, v_stock_dividend = self._average_dividend(dividends=stock.dividends)
                roi = self._return_on_investment(
                    price=stock.price,
                    v_cash=v_cash_dividend, v_stock=v_stock_dividend
                )
                yields = self._yields_convert_prices(v_cash=v_cash_dividend)
                v_yield = self._average_yield(v_cash=v_cash_dividend, price=stock.price)
                self._Results.append(
                    self._convert_to_model_data(
                        stock=stock,
                        v_cash=v_cash_dividend, v_stock=v_stock_dividend, v_yield=v_yield, roi=roi,
                        yields_convert_prices=yields
                    )
                )
            except Exception as e:
                print(f'calculate result error: {e}')
        return

    @property
    def result(self):
        if not self._Results:
            self._calculate_result()
        return self._Results







