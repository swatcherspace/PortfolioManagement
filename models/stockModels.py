from datetime import datetime
from pydantic import BaseModel
from datetime import date
from typing import Optional
class StocksModel(BaseModel):
    name:str
    type:str
    open:float
    high:float
    low:float
    close:float
    ltp:float
    volume:float
    lowPriceRange:float
    highPriceRange:float
    time_created:Optional[date]  
    time_updated:Optional[date] 
    
class Fundamentals(BaseModel):
    name:str
    shares_outstanding:int
    dividend_rate:float
    debt_to_equity:float
    book_value_per_share:float
    roe:float
    current_ratio:float
    pe_ratio:float
    pb_ratio:float #Price to Book Value
    market_cap:float
    earning_per_share:float
    industry_pe:float
    capped_type:str
    dividend_yield_percent:float
    face_value:float
    news:str
    pricebandupper:float
    total_sell_quantity:float 
    total_traded_val:float
    quantity_traded:float
    percentage_change:str
    ISINCode:str
    time_created:Optional[date]
    time_updated:Optional[date]
