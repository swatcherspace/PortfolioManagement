
import pandas as pd
import pickle
import random
def scrape_symbols():
    try:
        market_type = random.choice([ "NSE","NYSE"])
        #Wiki for reference/ may change later
        if market_type=="NYSE":
            data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
            symbol = data["Symbol"].to_list()
            name = data["Security"].to_list()
            name_to_symbol = dict(zip(name,symbol))
            symbol_to_name = dict(zip(symbol, name))
            # Store data (serialize)
            with open(market_type+'.pickle', 'wb') as handle:
                pickle.dump([name_to_symbol, symbol_to_name], handle, protocol=pickle.HIGHEST_PROTOCOL)
        elif market_type=="NSE":
            data = nse.get_stock_codes()
            symbol_to_name = dict(data)
            name_to_symbol = {v: k for k, v in symbol_to_name.items()}
            with open(market_type+'.pickle', 'wb') as handle:
                pickle.dump([name_to_symbol, symbol_to_name], handle, protocol=pickle.HIGHEST_PROTOCOL)   
        #Convert to list
        return "Success"
    except Exception as e:
        print(e)
    ...
