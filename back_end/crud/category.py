# back_end/crud/category.py

from sqlalchemy.orm import Session
from back_end import CategoryModel
from back_end.schema import category as schema


def is_category_in_db(db: Session, data: schema.Create):
    return get_category_by_name(db=db, name=data.name) is not None

# ------------------------------------ Create ------------------------------------
def create_category(db: Session, cat_create: schema.Create):
    """
    建立 單筆類別
    :param db:
    :param cat_create:
    :return:
    """
    db_cat = CategoryModel(**cat_create.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

def create_categories(db: Session, cats_create: list[schema.Create]):
    """
    建立 多筆類別
    :param db:
    :param cats_create:
    :return:
    """
    db_cats = [
        CategoryModel(**create.dict())
        for create in cats_create
        if not is_category_in_db(db=db, data=create)
    ]
    db.add_all(db_cats)
    db.commit()
    for obj in db_cats:
        db.refresh(obj)
    return db_cats

# ------------------------------------- Read -------------------------------------
def get_category_by_pid(db: Session, pid: int):
    """
    透過 主鍵 取得類別
    :param db:
    :param pid: 主鍵
    :return:
    """
    return db.query(CategoryModel).filter_by(id=pid).first()

def get_category_by_name(db: Session, name: str):
    """
    透過 類別名稱 取得類別
    :param db:
    :param name: 類別名稱
    :return:
    """
    return db.query(CategoryModel).filter_by(name=name).first()

def get_categories_of_twse(db: Session):
    """
    透過 twse 取得 上市類別
    :param db:
    :return:
    """
    return db.query(CategoryModel).filter_by(type='twse').all()

def get_categories_of_otc(db: Session):
    """
    透過 otc 取得 上櫃類別
    :param db:
    :return:
    """
    return db.query(CategoryModel).filter_by(type='otc').all()


# ------------------------------------ Update ------------------------------------

# ------------------------------------ Delete ------------------------------------





