
from http.client import HTTPException
import imp
# from select import select
import requests
from config import row2dict
from database.db import SessionLocal,init_schema,Stocks
import pandas as pd
from datetime import datetime
from models.stockModels import StocksModel

headersList = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/538.69 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/538.38",
        "Accept": "application/json",
        "Accept": "text/plain",
        "Content-Encoding": "br",
        "Connection": "close",
        "Content-Encoding": "gzip",
        "Content-Encoding": "deflate"
    }
class Stock:
    def __init__(self):
        try:
            self._session = init_schema()
        except Exception as e:
            raise HTTPException("Can't connect to the DB")

    async def get_stocks(self,name):
        data = self._session.query(Stocks).filter_by(name=name).first()
        return data
    
    async def get_quotes(self):
        db_data = {}
        data = self._session.query(Stocks).all()
        for i in data:
            data = row2dict(i)
            db_data[data["name"]] = data
        # Get the NSE stocks with highest values
        reqUrl1 = "http://localhost:3000/nse/get_top_value_stocks"
        # Get the NSE stocks with highest sold volume
        reqUrl2 = "http://localhost:3000/nse/get_top_volume_stocks"

        reqUrl1_payload_response = requests.request("GET", reqUrl1,  headers=headersList)
        reqUrl2_payload_response = requests.request("GET", reqUrl2,  headers=headersList)
        
        reqUrl1_api_data = reqUrl1_payload_response.json()
        Quotes = []
        for stock in reqUrl1_api_data["data"]:
            if stock["symbol"] in db_data:
                Quotes.append("{} in Top Value category".format(stock["symbol"]))
        
        reqUrl2_api_data = reqUrl2_payload_response.json()
        for stock in reqUrl2_api_data["data"]:
            if stock["symbol"] in db_data:
                Quotes.append("{} in Highest Sold Volume category".format(stock["symbol"]))

        return Quotes ,reqUrl1_api_data
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
        fundamental_payload = ""
        reqUrl = "http://localhost:3000/nse/get_quote_info?companyName={}".format(name)
        payload_response = requests.request("GET", reqUrl, data=fundamental_payload,  headers=headersList)
        data = payload_response.json()
        dt = datetime.now()    # for date and time
        ts = datetime.utcnow() 
        to_create = Stocks(
                name=data["data"][0]["symbol"],
                type=data["data"][0]["marketType"],
                open=float(data["data"][0]["open"].replace(",","")),
                high=float(data["data"][0]["dayHigh"].replace(",","")),
                low=float(data["data"][0]["dayLow"].replace(",","")),
                close=float(data["data"][0]["previousClose"].replace(",","")),
                ltp=float(data["data"][0]["lastPrice"].replace(",","")),
                volume=float(data["data"][0]["totalTradedVolume"].replace(",","")), 
                lowPriceRange=float(data["data"][0]["low52"].replace(",","")),
                highPriceRange=float(data["data"][0]["high52"].replace(",","")),
                time_created=dt, #traded date
                time_updated=ts
            )
        self._session.add(to_create)
        self._session.commit()
        return {"message": "Successfully Commited"}

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


         
async def get_stocks(name):
    stock = Stock()
    try:
        data = await stock.get_stocks(name)
        return data
    except Exception as e:
            raise HTTPException("Error getting stocks",e)
async def get_quotes():
    stock = Stock()
    try:
        data = await stock.get_quotes()
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