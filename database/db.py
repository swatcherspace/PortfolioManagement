from email.policy import default
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, JSON
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.sql import func
import uuid
from decouple import config
from sqlalchemy.orm import relationship
# Alter the below with your DB to begin with
SQLALCHEMY_DATABASE_URL = config("SQLALCHEMY_DATABASE_URL")  \
          +config("USERNAME")+":"+config("PASSWORD")+"@"+config("HOST") \
            +":"+config("PORT")+"/"+config("DB_NAME")
print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
## Global Session object
sess = {}

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())   
        
class Fundamentals(Base):
    __tablename__ = "fundamentals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    shares_outstanding = Column(Integer)
    dividend_rate = Column(Float)
    debt_to_equity = Column(Float)
    book_value_per_share = Column(Float)
    roe = Column(Float)
    current_ratio = Column(Float)
    pe_ratio = Column(Float)
    pb_ratio = Column(Float) #Price to Book Value
    market_cap = Column(Float)
    earning_per_share = Column(Float)
    industry_pe = Column(Float)
    capped_type = Column(String)
    dividend_yield_percent = Column(Float)
    face_value =  Column(Integer)
    news = Column(JSON)
    pricebandupper = Column(Float)
    total_sell_quantity = Column(Float) 
    total_traded_val = Column(Float)
    quantity_traded = Column(Float)
    percentage_change = Column(String)
    ISINCode = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    parent_id = Column(Integer, ForeignKey("stocks.id", ondelete='CASCADE'))

class Stocks(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
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
    
    child = relationship(Fundamentals, backref="stocks", passive_deletes=True)
class Cryptos(Base):
    __tablename__ = "cryptos"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    market = Column(String)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Float)
    lastPrice = Column(Float)
    bid = Column(Float)
    ask = Column(Float)
    day_change = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
sess = {}

def init_schema():
    global sess  # Use global keyword to modify the global variable
    try:
        if not isinstance(sess, dict):  # Check if sess is a dictionary
            raise ValueError("sess must be a dictionary")
        
        if not sess:
            Base.metadata.create_all(create_engine(SQLALCHEMY_DATABASE_URL))
            Session = sessionmaker(bind=create_engine(SQLALCHEMY_DATABASE_URL))
            sess["session"] = Session()
    except Exception as e:
        print(e)
    return sess.get("session")  # Return the session directly