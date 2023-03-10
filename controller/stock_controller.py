
from http.client import HTTPException
import imp
# from select import select
import requests
from config import row2dict
from database.db import  Fundamentals,init_schema,Stocks #Fundamentals
import pandas as pd
from datetime import datetime
from models.stockModels import StocksModel
from sqlalchemy import desc
import json
from nsetools import Nse
import yfinance as yf
from datetime import datetime, timedelta

nse = Nse()     
class Stock:
    def __init__(self):
        try:
            self._session = init_schema()
        except Exception as e:
            raise HTTPException("Can't connect to the DB")
    async def get_news(self,data):
        news = []
        if "news" in data:
            news_data = json.loads(data["news"])
            for i in news_data:
                # Fetch 10 latest news    
                if len(news) <= 10:
                    news.append((i["title"], i["publisher"], i["link"], i["providerPublishTime"]))
        return news

    async def get_fundamentals(self,name):
        data = self._session.query(Fundamentals).filter_by(name=name).first()
        data =  row2dict(data)
        data["news"] = await self.get_news(data)
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
            msg = await self.stock_to_table(name,payload_response, "NSE")
        else:
            payload_response = yf.Ticker(name).info
            msg = await self.stock_to_table(name,payload_response, "NYSE")
        return {"message": "Successfully Commited {}".format(msg)}

    async def filter_relevant_stocks_metrics(self,payload_response, news, market_type, name):
        # Currently operable only on NYSE, for NSE and BSE-> TODO
        # Filters all the information as per the metrics
        if "NSE" in market_type:
           pass

            
        if "NYSE" in market_type:

            metrics = [("marketCap","float"),("symbol","str"),("sharesOutstanding","int"),("dividendRate","float"),\
                    ("debtToEquity","float"),("bookValue","float"),("returnOnEquity","float"),("currentRatio","float"),\
                    ("trailingPE","float"),("currentPrice","float"),("trailingEps","float"),("dividendYield","float")]
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
            return
            #Data isn't fetched
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
                await self.fundametals_to_table(None, "NSE", None, name)
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
            if length < 3: #Only 3 latest entries could be present at a time
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

    async def get_symbols(self):
        #Wiki for reference/ may change later
        data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        #Convert to list
        symbol = data["Symbol"].to_list()
        name = data["Security"].to_list()
        sp = dict(zip(symbol, name))
        return sp

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
    
async def get_symbols():
    stock = Stock()
    try:
       data = await stock.get_symbols()
       return data
    except Exception as e:
        raise HTTPException("Error getting stock symbols",e)
    