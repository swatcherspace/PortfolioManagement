
from http.client import HTTPException
# from select import select
import requests
import pandas as pd
# from database.db import SessionLocal,Stock
# latest_payload = ""
#     # reqUrl = "https://groww.in/v1/api/stocks_data/v1/tr_live_prices/exchange/NSE/segment/CASH/{}/latest".format(name)
#     # latest_payload_response = requests.request("GET", reqUrl, data=latest_payload,  headers=headersList)
class AnalyzeMetrics:
    def __init__(self,stockName, earningPS, divYield, priceEarning, currentMarketCap, \
        preveviousMarketCap,tenYearProfit, fiveYearProfit, tenYearDividend, \
        fiveYearDividend, retainedProfit):
        self.__stockName = stockName
        self.__earningPS = earningPS#EPS %age
        self.__divYield = divYield #Dividend
        self.__priceEarning = priceEarning #PE
        self.__currentMarketCap = currentMarketCap
        self.__preveviousMarketCap = preveviousMarketCap
        self.__incrementalMaketCap = 0 # difference in M cap in X Years
        self.__tenYearProfit = tenYearProfit
        self.__fiveYearProfit = fiveYearProfit
        self.__tenYearDividend =  tenYearDividend
        self.__fiveYearDividend = fiveYearDividend
        self.__retainedProfit = retainedProfit
        self.__oneDollarTest = 0
        self.__peterLyncMetric = 0
        self.__retainedPercentage = 0 #close to 35 percent
    
    def getpeterLynchMetric(self):
        # Talks about stock correct val pricing index
        self._peterLyncMetric = int(self.__earningPS+self.__divYield/self.__priceEarning)
        if self._peterLyncMetric < 1:
            return "Over Values"
        elif self._peterLyncMetric==1:
            return "Fairly Valued"
        elif self._peterLyncMetric==2 or self._peterLyncMetric==3:
            return "Under Valued"
        return "Highly Under Valued"

    # def getbuffetDollarTest(self):
    #     self.__oneDollarTest = 
        
