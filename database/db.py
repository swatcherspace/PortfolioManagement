from email.policy import default
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.sql import func
import uuid
# # SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# # f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

SQLALCHEMY_DATABASE_URL = "postgresql://abhishek:password@localhost:5432/stocks_watcher"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
## Global Session object
sess = {}

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())   
class Stocks(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    ltp = Column(Float)
    volume = Column(Float)
    lowPriceRange = Column(Float)
    highPriceRange = Column(Float)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
        
# class Fundamentals(Base):
#     __tablename__ = "fundamentals"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String)
#     # pe_ratio = Column(float)
#     # pb_ratio = Column(float)
#     # market_cap = Column(float)
#     # book_value = Column(float)
#     # eps_ttm = Column(float)
#     # roe = Column(float)
#     # industry_pe = Column(float)
#     capped_type = Column(String)
#     # dividend_yield_percent = Column(float)
#     # debt_to_equity = Column(float)
#     face_value =  Column(Integer)
#     fundamentals = relationship("stock")
#     class Config:
#         orm_mode = True
def init_schema():
    try:
        if sess == {}:
            Base.metadata.create_all(create_engine(SQLALCHEMY_DATABASE_URL))
            session = sessionmaker(create_engine(SQLALCHEMY_DATABASE_URL))
            sess.update({"session": session()})
    except Exception as e:
        print(e)
    return sess['session']