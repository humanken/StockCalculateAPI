from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, func
from sqlalchemy.orm import relationship
from .db import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(5), index=True)
    name = Column(String(10), unique=True, index=True)
    sector_id = Column(Integer, index=True)

    # 對應 stocks
    stocks = relationship("StockModel", back_populates="category")

    update = Column(
        DateTime,
        default=datetime.now().replace(microsecond=0),
        onupdate=datetime.now().replace(microsecond=0)
    )


class StockModel(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)

    # 對應 categories
    cat_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("CategoryModel", back_populates="stocks")

    number = Column(String(10), unique=True, index=True)
    name = Column(String(20), unique=True, index=True)
    price = Column(Float, nullable=True)

    # 對應 dividends
    dividends = relationship("DividendModel", back_populates="stocks")

    update = Column(
        DateTime,
        default=datetime.now().replace(microsecond=0),
        onupdate=datetime.now().replace(microsecond=0)
    )


class DividendModel(Base):
    __tablename__ = "dividends"

    id = Column(Integer, primary_key=True, index=True)

    # 對應 stocks
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    stocks = relationship("StockModel", back_populates="dividends")

    year = Column(String(6))
    cash = Column(Float, nullable=True, comment="現金股利")
    stock = Column(Float, nullable=True, comment="股票股利")

    update = Column(
        DateTime,
        default=datetime.now().replace(microsecond=0),
        onupdate=datetime.now().replace(microsecond=0)
    )


