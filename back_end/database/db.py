from os import environ
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# SQLALCHEMY_DATABASE_URL = "sqlite:///./back_end/database/stock_app.db"
SQLALCHEMY_DATABASE_URL = \
    f"mysql+mysqldb://" \
    f"{environ.get('MYSQL_USER')}:{environ.get('MYSQL_PASSWORD')}@db/" \
    f"{environ.get('MYSQL_NAME')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=0, max_overflow=-1,
    connect_args={"check_same_thread": False}
)
# connect_args={"check_same_thread": False} 僅用在sqlite

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    """
    取得database session，並傳給函數執行資料庫操作，結束將關閉
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DBContextManager:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()










