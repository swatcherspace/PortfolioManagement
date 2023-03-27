
import pandas as pd
from api.stocks import Stocks
import pickle
import nsetools
from controller.stock_controller import nse 
from rocketry import Rocketry
from rocketry.conds import monthly
import random
app = Rocketry()

# Create some tasks:

@app.task(monthly.after("1"))
def scrape_symbols():
    try:
        print("Hi")
        market_type = random.choice(["NSE", "NYSE"])
        #Wiki for reference/ may change later
        if market_type=="NYSE":
            data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
            symbol = data["Symbol"].to_list()
            name = data["Security"].to_list()
            sp = dict(zip(symbol, name))
            # Store data (serialize)
            with open(market_type+'.pickle', 'wb') as handle:
                pickle.dump(sp, handle, protocol=pickle.HIGHEST_PROTOCOL)
        elif market_type=="NSE":
            data = nse.get_stock_codes()
            data = dict(data)
            with open(market_type+'.pickle', 'wb') as handle:
                pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)   
        #Convert to list
        return "Success"
    except Exception as e:
        print(e)
    ...

