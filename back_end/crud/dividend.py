# back_end/crud/dividend.py

from sqlalchemy import desc
from sqlalchemy.orm import Session
from back_end import DividendModel
from back_end.schema import dividend as schema


def is_dividend_of_year_exist(instances: list[DividendModel], year: str):
    return next((instance for instance in instances if instance.year == year), False)

# ------------------------------------ Create ------------------------------------
def create_dividends(db: Session, dividends_create: list[schema.Create]):
    """
    建立 多筆股票
    :param db:
    :param dividends_create:
    :return:
    """
    db_dividends = [
        DividendModel(**create.dict())
        for create in dividends_create
    ]
    db.add_all(db_dividends)
    db.commit()
    for obj in db_dividends:
        db.refresh(obj)
    return db_dividends

# ------------------------------------- Read -------------------------------------
def get_dividend_by_pid(db: Session, pid: int):
    """
    透過 股票主鍵 和 年份 取得股利
    :param db:
    :param pid: 主鍵
    :return:
    """
    return db.query(DividendModel).filter_by(id=pid).first()


def get_dividend_by_stock_id_year(db: Session, stock_id: int, year: str):
    """
    透過 股票主鍵 和 年份 取得股利
    :param db:
    :param stock_id: 股票主鍵
    :param year: 年份
    :return:
    """
    return db.query(DividendModel).filter_by(stock_id=stock_id).filter_by(year=year).first()


def get_dividends_by_stock(db: Session, stock_id: int, limit: int = 10):
    """
    透過 股票主鍵 取得股利
    :param db:
    :param stock_id: 股票主鍵
    :param limit: 一次取得最多筆數
    :return:
    """
    return db.query(DividendModel).filter_by(stock_id=stock_id).order_by("year").limit(limit).all()


def get_latest_update_time(db: Session):
    return db.query(DividendModel).order_by(desc('update')).first().update


# ------------------------------------ Update ------------------------------------
def update_dividends(db: Session, instances: list[DividendModel], dividends_update: list[schema.Update]):
    """
    更新 指定年份的股利
    :param db:
    :param instances:
    :param dividends_update:
    :return:
    """
    db_dividends = []
    for instance, update in zip(instances, dividends_update):
        for key, value in update.dict().items():
            setattr(instance, key, value)
        db_dividends.append(instance)
    db.add_all(db_dividends)
    db.commit()
    for obj in db_dividends:
        db.refresh(obj)
    return db_dividends


# ------------------------------------ Delete ------------------------------------
def delete_dividend(db: Session, dividend_delete: schema.Delete):
    """
    刪除股利
    :param db:
    :param dividend_delete:
    :return:
    """
    if instance := get_dividend_by_stock_id_year(
            db=db, stock_id=dividend_delete.stock_id, year=dividend_delete.year
    ):
        db.delete(instance)
        db.commit()
        db.refresh(instance)
    return instance





