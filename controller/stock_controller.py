
import imp
import json
import sys
from datetime import datetime, timedelta
from http.client import HTTPException
import pickle
from pathlib import Path
import pandas as pd
# from select import select
import requests
import yfinance as yf
from nsetools import Nse
from sqlalchemy import desc

from config import row2dict
from database.db import Fundamentals, Stocks, init_schema  # Fundamentals
from models.stockModels import StocksModel
from decouple import Config
from utils import LDS
nse = Nse()     

class Stock:
    def __init__(self):
        try:
            self._session = init_schema()
        except Exception as e:
            raise HTTPException("Can't connect to the DB")
    @staticmethod
    async def get_news(data):
        news_data = json.loads(data["news"])
        return news_data

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
        
    async def get_fundamentals(self,name):
        data = self._session.query(Fundamentals).filter_by(name=name).first()
        data =  row2dict(data)
        cash_flow = await Stock.get_cash_flow(name)
        data['cashflow'] = cash_flow
        return data
    
    async def get_stocks(self,name):
        data = self._session.query(Stocks).filter_by(name=name).first()
        return data
    
    async def get_quotes(self, name):
        try:
            # process relevant info about Fundamentals
            data = self._session.query(Fundamentals).filter_by(name=name).order_by(desc(Fundamentals.time_created)).all()
            result = []
            for i in data:
                result.append(row2dict(i))
            news_data = []    
            for i in result:    
                news_data.append(await self.get_news(i))
            return news_data
        except Exception as a:
            print("Table Not present hence creating..",a)

    async def stock_to_table(self, name,payload_response, market_type):
        if "NSE" in market_type:
            dt = datetime.now()    # for date and time
            ts = datetime.utcnow()
            try:
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
            except Exception as e:
                return {"message": "KeyError in NSE".format(e)}
                
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
        return name

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
            print(payload_response)
            msg = await self.stock_to_table(name,payload_response, "NSE")
        else:
            payload_response = yf.Ticker(name).info
            print(payload_response)
            msg = await self.stock_to_table(name,payload_response, "NYSE")
        return {"message": "Successfully Commited {}".format(msg)}
    @staticmethod
    def filter_metrics(payload_response,metrics):
        symbols_present = {}
        for i in metrics:
            if i[0] not in payload_response:
                if i[1]=="str":
                    symbols_present[i[0]] = ""
                elif i[1]=="float":
                    symbols_present[i[0]] = 0.0
                elif i[1]=="int":
                    symbols_present[i[0]] = 1
                continue
            symbols_present[i[0]] = payload_response[i[0]]
        return symbols_present
    async def filter_relevant_stocks_metrics(self,payload_response, news, market_type, name):
        # Currently operable only on NYSE, for NSE and BSE-> TODO
        # Filters all the information as per the metrics
        if "NSE" in market_type:
            dt = datetime.now()    # for date and time
            ts = datetime.utcnow()
            metrics = [('pricebandupper','float'),('totalSellQuantity','float') ,('totalTradedValue','float'),('quantityTraded','float'),('pChange','str'),('isinCode','str')]
            symbols_present = Stock.filter_metrics(payload_response, metrics) 
            metrics_data = Fundamentals(
                name = payload_response["symbol"],
                pricebandupper = payload_response["pricebandupper"],
                total_sell_quantity = symbols_present["totalSellQuantity"],
                total_traded_val = symbols_present["totalTradedValue"],
                quantity_traded = symbols_present["quantityTraded"],
                percentage_change = symbols_present["pChange"],
                ISINCode = symbols_present["isinCode"],
                news = json.dumps(news,default=str)
            )
            return metrics_data
            
        if "NYSE" in market_type:

            metrics = [("marketCap","float"),("symbol","str"),("sharesOutstanding","int"),("dividendRate","float"),\
                    ("debtToEquity","float"),("bookValue","float"),("returnOnEquity","float"),("currentRatio","float"),\
                    ("trailingPE","float"),("currentPrice","float"),("trailingEps","float"),("dividendYield","float")]
            symbols_present = Stock.filter_metrics(payload_response,metrics)
            cap_type = ""
            if symbols_present["marketCap"]> 20000:
                cap_type = "Large-Cap"
            elif symbols_present["marketCap"]< 5000:
                cap_type = "Small-Cap"
            else:
                cap_type = "Mid-Cap"
            dt = datetime.now()    # for date and time
            ts = datetime.utcnow()
            metrics_data = Fundamentals(
                name = symbols_present["symbol"],
                shares_outstanding = symbols_present["sharesOutstanding"],
                dividend_rate = symbols_present["dividendRate"],
                debt_to_equity = symbols_present["debtToEquity"],
                book_value_per_share = symbols_present["bookValue"],
                roe = symbols_present["returnOnEquity"],
                current_ratio = symbols_present["currentRatio"],
                pe_ratio = symbols_present["trailingPE"],
                pb_ratio = symbols_present["currentPrice"]/symbols_present["trailingEps"],
                market_cap = symbols_present["marketCap"],
                earning_per_share = symbols_present["trailingEps"],
                industry_pe = float(0.0),
                capped_type = cap_type,
                dividend_yield_percent = symbols_present["dividendYield"],
                face_value = 0,
                news = json.dumps(news,default=str),
                time_created=dt, #traded date
                time_updated=ts
            )
            return metrics_data
    async def fundametals_to_table(self, payload_response, market_type, news, name):
        # Populated Fundamentals table based on market_type and recieved metrics
        # For NYSE
        if "NSE" in market_type:
            to_create = await self.filter_relevant_stocks_metrics(payload_response,news,market_type, name)
        if "NYSE" in market_type:
            to_create = await self.filter_relevant_stocks_metrics(payload_response,news,market_type, name)

        self._session.add(to_create)
        self._session.commit()    
        return
    async def fundamental_insertion(self,col,name):
        # Fetched the data from nysetool/third party and updated it's fundamentals to the DB
        stock_db_data = row2dict(col)
        if stock_db_data["name"]==name:
            if nse.is_valid_code(name):
                #Need to add the fetcher 
                payload_response = nse.get_quote(name)
                news = payload_response["purpose"]
                await self.fundametals_to_table(payload_response, "NSE", news, name)
                return {"message": "Successfully create_fundamentals Commited"}
            if float(yf.Ticker(name).info['regularMarketPrice']):
                payload_response = yf.Ticker(name).info
                news = yf.Ticker(name).news
                
                await self.fundametals_to_table(payload_response, "NYSE", news, name)
                return {"message": "Successfully create_fundamentals Commited"}
    async def create_fundamentals(self,name):
        try:
            col = self._session.query(Stocks).filter_by(name=name).first()
            f_data = self._session.query(Fundamentals.id).filter_by(name=name).all()
            length = len(f_data)
            print(f_data, length)
            if length < 2: #Only 1 latest entries could be present at a time
                return await self.fundamental_insertion(col,name)
            else:
                # Delete older entries 
                count = 0
                for id in f_data:
                    if count < 2:                        
                        self._session.query(Fundamentals).filter_by(id=id[0]).delete()
                        count += 1
                #Complete the above entry
                return await self.fundamental_insertion(col,name)
        except AttributeError as a:
            print("Table Not present",a)

    async def delete_stocks(self,name):
        self._session.query(Stocks).filter_by(name=name).delete()
        self._session.commit()
        return {"message": "Successfully Deleted"}

    async def upload_file(name, contents):
        #todo 
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
    
