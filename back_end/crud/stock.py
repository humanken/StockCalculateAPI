# back_end/crud/StockModel.py

from sqlalchemy import desc
from sqlalchemy.orm import Session
from back_end import StockModel, CategoryModel
from back_end.schema import stock as schema


def is_stock_in_db(db: Session, data: schema.Create or schema.Update):
    stock = get_stock_by_number(db=db, number=data.number)
    return stock if stock else False


# ------------------------------------ Create ------------------------------------
def create_stocks(db: Session, stocks_create: list[schema.Create]):
    """
    建立 多筆股票
    :param db:
    :param stocks_create:
    :return:
    """
    db_stocks = [
        StockModel(**create.dict())
        for create in stocks_create
        if not is_stock_in_db(db=db, data=create)
    ]
    db.add_all(db_stocks)
    db.commit()
    for obj in db_stocks:
        db.refresh(obj)
    return db_stocks


# ------------------------------------- Read -------------------------------------
def get_stock_by_pid(db: Session, pid: int):
    """
    透過 主鍵 取得股票
    :param db:
    :param pid: 主鍵
    :return:
    """
    return db.query(StockModel).filter_by(id=pid).first()


def get_stock_by_number(db: Session, number: str):
    """
    透過 股票代碼 取得股票
    :param db:
    :param number: 股票代碼
    :return:
    """
    return db.query(StockModel).filter_by(number=number).first()


def get_stocks(db: Session, skip: int = 0, limit: int = 1000, excludes: [int] = None):
    """
    取得所有股票
    :param db:
    :param skip: 跳過筆數
    :param limit: 一次取得最多筆數
    :param excludes: 類別篩選
    :return:
    """
    if excludes:
        # 取得 不是excludes內的股票
        db_filter = db.query(StockModel).join(CategoryModel).filter(
            CategoryModel.sector_id.notin_([ex for ex in excludes])
        )
    else:
        db_filter = db.query(StockModel)
    return db_filter.offset(skip).limit(limit).all(), len(db_filter.all())


def get_latest_update_time(db: Session):
    return db.query(StockModel).order_by(desc('update')).first().update


# ------------------------------------ Update ------------------------------------
def update_prices(db: Session, stocks_update: list[schema.Update]):
    """
    更新 股票現價
    :param db:
    :param stocks_update:
    :return:
    """

    db_stocks = [
        setattr(instance, 'price', update.price) or instance
        for update in stocks_update
        if (instance := is_stock_in_db(db=db, data=update))
    ]
    db.add_all(db_stocks)
    db.commit()
    for obj in db_stocks:
        db.refresh(obj)
    return db_stocks


# ------------------------------------ Delete ------------------------------------

