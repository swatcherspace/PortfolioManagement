
from http.client import HTTPException
import imp
# from select import select
import requests
from config import row2dict
from database.db import  Fundamentals, SessionLocal,init_schema,Stocks #Fundamentals
import pandas as pd
from datetime import datetime
from models.stockModels import StocksModel
import json
from nsetools import Nse
import yfinance as yf
headersList = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/538.69 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/538.38",
        "Accept": "application/json",
        "Accept": "text/plain",
        "Content-Encoding": "br",
        "Connection": "close",
        "Content-Encoding": "gzip",
        "Content-Encoding": "deflate"
    }
nse = Nse()     
class Stock:
    def __init__(self):
        try:
            self._session = init_schema()
        except Exception as e:
            raise HTTPException("Can't connect to the DB")
    async def get_fundamentals(self,name):
        data = self._session.query(Stocks).filter_by(name=name).first()
        return data
    
    async def get_stocks(self,name):
        data = self._session.query(Stocks).filter_by(name=name).first()
        return data
    
    async def get_quotes(self, name):
        try:
            pass           
        except AttributeError as a:
            print("Table Not present hence creating..")
    async def stock_to_table(self, payload_response, market_type):
        if "NSE" in market_type:
            dt = datetime.now()    # for date and time
            ts = datetime.utcnow()
            to_create = Stocks(
                    name=payload_response["symbol"],
                    type=payload_response["marketType"],
                    open=float(payload_response["open"]),
                    high=float(payload_response["dayHigh"]),
                    low=float(payload_response["dayLow"]),
                    close=float(payload_response["previousClose"]),
                    ltp=float(payload_response["lastPrice"]),
                    volume=float(payload_response["totalTradedVolume"]), 
                    lowPriceRange=float(payload_response["low52"]),
                    highPriceRange=float(payload_response["high52"]),
                    time_created=dt, #traded date
                    time_updated=ts
                )

        elif "NYSE" in market_type:
            dt = datetime.now()    # for date and time
            ts = datetime.utcnow()
            to_create = Stocks(
                    name=payload_response["symbol"],
                    type=payload_response["sector"],
                    open=float(payload_response["open"]),
                    high=float(payload_response["dayHigh"]),
                    low=float(payload_response["dayLow"]),
                    close=float(payload_response["previousClose"]),
                    ltp=float(payload_response["currentPrice"]),
                    volume=float(payload_response["volume"]), 
                    lowPriceRange=float(payload_response["fiftyTwoWeekLow"]),
                    highPriceRange=float(payload_response["fiftyTwoWeekHigh"]),
                    time_created=dt, #traded date
                    time_updated=ts
                )
        else:
            return {"message": "Ambiguous Data recieved"}
        self._session.add(to_create)
        self._session.commit()
        return

    async def create_stocks(self,name):
        try:
            col = self._session.query(Stocks).filter_by(name=name).first()
            stock_db_data = row2dict(col)
            if stock_db_data["name"]==name:
                return {"message": "Entry Already Present"}   
        except AttributeError as a:
            print("Table Not present hence creating..")
        except Exception as e:
            raise HTTPException("Error getting stocks from DB",e)  
        if nse.is_valid_code(name):
            payload_response = nse.get_quote(name)
            msg = await self.stock_to_table(payload_response, "NSE")

        elif float(yf.Ticker(name).info['regularMarketPrice']):
            payload_response = yf.Ticker(name).info
            msg = await self.stock_to_table(payload_response, "NYSE")
        return {"message": "Successfully Commited {}".format(msg)}
    async def fundametals_to_table(self, payload_response, market_type, news):
        if "NYSE" in market_type:
            dt = datetime.now()    # for date and time
            ts = datetime.utcnow()
            cap_type = ""
            if payload_response["marketCap"]> 20000:
                cap_type = "Large-Cap"
            elif payload_response["marketCap"]< 5000:
                cap_type = "Small-Cap"
            else:
                cap_type = "Mid-Cap"
            to_create = Fundamentals(
                name = payload_response["symbol"],
                shares_outstanding = payload_response["sharesOutstanding"],
                dividend_rate = payload_response["dividendRate"],
                debt_to_equity = payload_response["debtToEquity"],
                book_value_per_share = payload_response["bookValue"],
                roe = payload_response["returnOnEquity"],
                current_ratio = payload_response["currentRatio"],
                pe_ratio = payload_response["trailingPE"],
                pb_ratio = payload_response["currentPrice"]/payload_response["trailingEps"],
                market_cap = payload_response["marketCap"],
                earning_per_share = payload_response["trailingEps"],
                industry_pe = float(0.0),
                capped_type = cap_type,
                dividend_yield_percent = payload_response["dividendYield"],
                face_value = 0,
                news = json.dumps(news,default=str),
                time_created=dt, #traded date
                time_updated=ts
            )
        self._session.add(to_create)
        self._session.commit()    
        return

    async def fetch_fundamentals(self,name):
        try:
            col = self._session.query(Stocks).filter_by(name=name).first()
            stock_db_data = row2dict(col)
            if stock_db_data["name"]==name:
                if float(yf.Ticker(name).info['regularMarketPrice']):
                    payload_response = yf.Ticker(name).info
                    news = yf.Ticker(name).news
                    await self.fundametals_to_table(payload_response, "NYSE", news)
                elif nse.is_valid_code(name):
                    pass
            return {"message": "Successfully fetch_fundamentals Commited"} 
        except AttributeError as a:
            print("Table Not present",a)

    async def delete_stocks(self,name):
        self._session.query(Stocks).filter_by(name=name).delete()
        self._session.commit()
        return {"message": "Successfully Deleted"}

    async def upload_file(name, contents):
        xl_file = pd.read_csv("/stocks.csv")
        xl_file.head()
        xl_file.dropna(inplace=True)
        xl_file.columns = xl_file.iloc[0]
        xl_file = xl_file[1:]



async def get_fundamentals(name):
    stock = Stock()
    try:
        data = await stock.get_fundamentals(name)
        return data
    except Exception as e:
            raise HTTPException("Error getting fundamentals",e)

async def get_stocks(name):
    stock = Stock()
    try:
        data = await stock.get_stocks(name)
        return data
    except Exception as e:
            raise HTTPException("Error getting stocks",e)
async def get_quotes(name):
    stock = Stock()
    try:
        data = await stock.get_quotes(name)
        return data
    except Exception as e:
            raise HTTPException("Error getting stocks",e)

async def create_stocks(name):
    stock = Stock()
    try:
        data = await stock.create_stocks(name)
        return data
    except Exception as e:
        raise HTTPException("Error creating stocks",e)

async def fetch_fundamentals(name):
    stock = Stock()
    try:
        data = await stock.fetch_fundamentals(name)
        return data
    except Exception as e:
        raise HTTPException("Error creating stocks",e)

async def upload_file(name, contents):
    stock = Stock()
    try:
        data = await stock.upload_file(name, contents)
        return data
    except Exception as e:
        raise HTTPException("Error creating stocks",e)


async def delete_stocks(name):
    stock = Stock()
    try:
        data = await stock.delete_stocks(name)
        return data
    except Exception as e:
        raise HTTPException("Error deleting stocks",e)