import hmac
import hashlib
import base64
import json
import time
import requests

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, message, from_email, to_email, password):
    # Create a message container
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Add the message body
    msg.attach(MIMEText(message, 'plain'))

    # Create an SMTP object
    smtp_obj = smtplib.SMTP('smtp.outlook.com', 587)

    # Start the SMTP connection
    smtp_obj.ehlo()
    smtp_obj.starttls()
    smtp_obj.ehlo()

    # Login to the SMTP server
    smtp_obj.login(from_email, password)

    # Send the email
    smtp_obj.sendmail(from_email, to_email, msg.as_string())

    # Close the connection
    smtp_obj.quit()
def Send_Email(Token):
    # Example usage in your own script
    subject = f'Important'
    message = f'{Token} Needs a reinvestment'
    from_email = "anshu98@outlook.com"
    to_email = "anshu98@outlook.com"
    password = "Jarvis@1234"
    message_id = '<1234567890abcdef@example.com>'
    send_email(subject, message, from_email, to_email, password)

def GET_Headers(json_body):
    # Enter your API Key and Secret here. If you don't have one, you can generate it from the website.
    key = "KEY"
    secret = "SECRET-KEY"

    secret_bytes = bytes(secret,  encoding='utf-8')
    signature = hmac.new(secret_bytes, json_body.encode(),
                         hashlib.sha256).hexdigest()
    # Generating a timestamp
    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': key,
        'X-AUTH-SIGNATURE': signature
    }
    return headers


def API_CALL(url):
    data = {
        "timestamp": int(round(time.time() * 1000)),
    }
    data = json.dumps(data, separators=(',', ':'))
    headers = GET_Headers(data)
    response = requests.post(url, data=data, headers=headers)
    data = response.json()
    return data


def Get_User_Info():
    url = "https://api.coindcx.com/exchange/v1/users/info"
    return API_CALL(url)


def Get_Balance_Info():
    url = "https://api.coindcx.com/exchange/v1/users/balances"
    balance = API_CALL(url)
    return balance


def Place_Order(price, total_quantity, side, order_type, is_multiple_order, orders, market_pair):
    print(is_multiple_order)
    if is_multiple_order:
        print("Hi")
        url = "https://api.coindcx.com/exchange/v1/orders/create_multiple"
        body = {"orders": orders}
        json_body = json.dumps(body, separators=(',', ':'))
        headers = GET_Headers(json_body)
        response = requests.post(url, data=body, headers=headers)
        data = response.json()
    else:
        url = "https://api.coindcx.com/exchange/v1/orders/create"
        body = {
            "side": side,  # Toggle between 'buy' or 'sell'.
            "order_type": order_type, # Toggle between a 'market_order' or 'limit_order'.            
            "market": market_pair, # Replace 'SNTBTC' with your desired market pair.
            "price_per_unit": price,  # This parameter is only required for a 'limit_order'
            "total_quantity": total_quantity,  # Replace this with the quantity you want
            "client_order_id": "2022.02.14-btcinr_1", # Replace this with the client order id you want
            "timestamp": int(round(time.time() * 1000)),
        }
        json_body = json.dumps(body, separators=(',', ':'))
        headers = GET_Headers(json_body)
        response = requests.post(url, data=json_body, headers=headers)
        data = response.json()
    return data


def Multiple_Order_status(ids):
    body = {
        # ["8a2f4284-c895-11e8-9e00-5b2c002a6ff4", "8a1d1e4c-c895-11e8-9dff-df1480546936"], # Array of Order ids
        "ids": ids,
        # "client_order_ids": ["2022.02.14-btcinr_1", "2022.02.14-btcinr_2"], # Array of Client Order ids
    }
    url = "https://api.coindcx.com/exchange/v1/orders/status_multiple"
    return API_CALL(url, body, False)


last_price = {}
def Get_Latest_Price(coin, currency):
    import requests
    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={coin}&to_currency={currency}&apikey=XAGTPID8LTX34JMJ'
    r = requests.get(url)
    data = r.json()
    return float(data['Realtime Currency Exchange Rate']['8. Bid Price'])

def Process_Order(token, currency):  # 'BTC'
    global last_price
    while True:
        price = Get_Latest_Price(token, currency)
        print(price)
        if token in last_price:
            # Gains by 15 more points may change later
            if last_price[token] < price and 0.15 < price - last_price[token]:
                print("Place the buy order", price)
                price = 1
                quantity = 1
                side = "buy"
                order_type = 'market_order' #'market_order' or 'limit_order', 
                is_multiple_order = False 
                orders = None # Since not a multiple order
                market_pair = "BTCUSDT" # Market type conversion
                resp = Place_Order(price, quantity, side, order_type, is_multiple_order, orders, market_pair)   
                print(resp) 
                last_price[token] = price
            # Loses by 5 more points may change later
            elif last_price[token] > price and 0.05 < abs(price - last_price[token]): #Sell 
                print("Place the sell order",price)
                price = 1
                quantity = 1
                side = "sell"
                order_type = 'market_order' #'market_order' or 'limit_order', 
                is_multiple_order = False 
                orders = None # Since not a multiple order
                market_pair = "BTCUSDT" # Market type conversion
                resp = Place_Order(price, quantity, side, order_type, is_multiple_order, orders, market_pair)   
                print(resp) 
                last_price[token] = price
        else:
            last_price[token] = price

        time.sleep(0.1 * 60)

def Check_Portfolio():
    global currency
    # if len(currency)== 
    portfolio = Get_Balance_Info()
    token = []
    for currency_detail in portfolio:
        name = currency_detail["currency"]
        locked_balance = float(currency_detail['locked_balance'])
        if locked_balance <= float(0):
            if name=="ETHW":
                continue
            token.append(name)
    print(token)
    return Send_Email(str(', '.join(token)))  


# print(Get_User_Info())
# print(Check_Portfolio())
# print(Send_Email("BTC"))
# print(Get_Balance_Info())
# print(Get_Latest_Price('BTC', 'INR'))
# print(Process_Order('BTC', 'USDT'))
# print(Place_Order(50000, 100, "buy", "limit_order", False, None, 'BTCUSDT'))
