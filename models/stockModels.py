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
    class Config:
        orm_mode = True
