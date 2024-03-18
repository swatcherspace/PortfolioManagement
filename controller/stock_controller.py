import json
from http.client import HTTPException
import pickle
from nsepython import *
import pandas as pd
# from select import select
import requests
from utils.utils import *
from sqlalchemy.exc import SQLAlchemyError
import yfinance as yf
from nsetools import Nse
from sqlalchemy import desc
from config import row2dict
from database.db import Fundamentals, Stocks,Cryptos, init_schema  # Fundamentals
from datetime import datetime
nse = Nse()     

# Create an asynchronous session

class Stock:
    def __init__(self):
        try:
            self._session = init_schema()
        except Exception as e:
            raise HTTPException("Can't connect to the DB")
    def add(self, obj):
        self._session.add(obj)

    def commit(self):
        self._session.commit()
    @staticmethod
    async def get_cash_flow(symbol):
        # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
        url = 'https://www.alphavantage.co/query?function=CASH_FLOW&symbol='+symbol+'&apikey='+'API-KEY-VALUES'
        r = requests.get(url)
        data = r.json()['annualReports']
        operating_cash_flow_data = []
        for annualreport in data:
          operating_cash_flow_data.append(int(annualreport['operatingCashflow']))
        if LDS(operating_cash_flow_data) > 2:
            return True
        else:
            return False
        
    async def get_stocks(self,name):
        data = self._session.query(Stocks).filter_by(name=name).first()
        return data
    async def create_crypto(self,payload_response,name):
        dt = datetime.now()
        ts = datetime.utcnow()
         # Create new entry
        new_crypto = Cryptos(
            name=name,
            market=payload_response.get("market"),
            low=payload_response.get("low"),
            high=payload_response.get("high"),
            volume=payload_response.get("volume"),
            lastPrice=payload_response.get("last_price"),
            bid=payload_response.get("bid"),
            ask=payload_response.get("ask"),
            day_change=payload_response.get("change_24_hour"),
            timestamp=datetime.fromtimestamp(payload_response.get("timestamp")),
            time_created=dt,
            time_updated=ts,
        )
        self._session.add(new_crypto)
        self._session.commit()
    async def update_crypto(self,payload_response,crypto):
        # Update existing entry
        dt = datetime.now()
        ts = datetime.utcnow()
        try:
            crypto.market = payload_response.get("market")
            crypto.low = payload_response.get("low")
            crypto.high = payload_response.get("high")
            crypto.volume = payload_response.get("volume")
            crypto.lastPrice = payload_response.get("last_price")
            crypto.bid = payload_response.get("bid")
            crypto.ask = payload_response.get("ask")
            crypto.day_change = payload_response.get("change_24_hour")
            crypto.timestamp = datetime.fromtimestamp(payload_response.get("timestamp"))
            crypto.time_updated = ts
            # Commit changes to the database
            self._session.commit()
        except SQLAlchemyError as e:
            raise HTTPException(500,f"Error updating crypto: {e}")

    async def CreateOrUpdateStockOrCrypto(self, name,payload_response, market_type):
        if not payload_response:
            return{"message": f"Error getting data from wallet for: {name}"}
        if "NSE" in market_type:
            dt = datetime.now()    # for date and time
            ts = datetime.utcnow()
            try:
                to_create = Stocks(
                    name=payload_response["info"]["symbol"],
                    type=market_type,
                    open=float(payload_response["priceInfo"]["open"]),
                    high=float(payload_response["priceInfo"]["intraDayHighLow"]["max"]),
                    low=float(payload_response["priceInfo"]["intraDayHighLow"]["min"]),
                    close=float(payload_response["priceInfo"]["close"]),
                    ltp=float(payload_response["priceInfo"]["lastPrice"]),
                    volume=float(payload_response["preOpenMarket"]["totalTradedVolume"]),
                    lowPriceRange=float(payload_response["priceInfo"]["weekHighLow"]["min"]),
                    highPriceRange=float(payload_response["priceInfo"]["weekHighLow"]["max"]),
                    time_created=dt,
                    time_updated=datetime.strptime(payload_response["metadata"]["lastUpdateTime"], "%d-%b-%Y %H:%M:%S")
                )
                self._session.add(to_create)
                self._session.commit()
            except Exception as e:
                return {"message": "KeyError in NSE".format(e)}
        elif "CRYPTO" in market_type:
            dt = datetime.now()
            ts = datetime.utcnow()
            name = payload_response.get("name")
            crypto = None  
            try:
                crypto = self._session.query(Cryptos).filter(Cryptos.name == name).first()

            except AttributeError:
                print("Table Not present hence creating..",name)
            except SQLAlchemyError as e:
                raise HTTPException(status_code=500, detail=f"Error getting data from DB: {e}")

            try:
                if crypto:    
                    await self.update_crypto(payload_response,crypto)
                else:
                    await self.create_crypto(payload_response,name)
            except SQLAlchemyError as e:
                raise HTTPException(500, f"Error updating or creating entry: {e}")

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
            self._session.add(to_create)
            self._session.commit()
        else:
            return {"message": "Ambiguous Data recieved"}
        
        return name

    async def create_stocks(self,name, market_type):
        if "crypto" in market_type.lower():
            #CoinDCX or any suitable exchange API
            wallet_data = Get_Balance_Info()
            coins = {}
            for coin in wallet_data:
                name = coin["currency"]
                balance = float(coin['balance'])
                locked_balance = float(coin['locked_balance'])
                if balance > float(0) or locked_balance > float(0):
                    coins[name] = ""
            for coin in coins.keys():
                for chunk in process_large_json_resp(Get_Data):
                    if coin in chunk.get("market") and coin != "INR":
                        chunk["name"] = coin
                        coins[coin] = chunk
            for coin in coins:
                msg = await self.CreateOrUpdateStockOrCrypto(name,coins[coin], "CRYPTO")
            
        else:
            try:
                col = self._session.query(Stocks).filter_by(name=name).first()
                stock_db_data = row2dict(col)
                if stock_db_data["name"]==name:
                    return {"message": "Entry Already Present"}   
            except AttributeError as a:
                print("Table Not present hence creating..")
            except Exception as e:
                raise HTTPException("Error getting stocks from DB",e)
            if "nse" in market_type.lower():
                payload_response = nse_eq(name)
                msg = await self.CreateOrUpdateStockOrCrypto(name,payload_response, "NSE")
            elif "nyse" in market_type.lower():
                payload_response = yf.Ticker(name).info
                msg = await self.CreateOrUpdateStockOrCrypto(name,payload_response, "NYSE")            
        return {"message": "Successfully Commited {}".format(msg)}
    

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

async def create_stocks(name, market_type):
    stock = Stock()
    try:
        data = await stock.create_stocks(name, market_type)
        return data
    except Exception as e:
        raise HTTPException("Error creating stocks",e)

async def create_fundamentals(name):
    stock = Stock()
    try:
        data = await stock.create_fundamentals(name)
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
    
async def get_symbols(market_type):
    stock = Stock()
    try:
       # Load data (deserialize)
        with open(market_type.upper()+'.pickle', 'rb') as handle:
            unserialized_data = pickle.load(handle)
        return unserialized_data
    except Exception as e:
        raise HTTPException("Error getting stock symbols",e)
    
