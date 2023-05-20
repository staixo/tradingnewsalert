import requests
import datetime as dt
import json
import twilio.rest as client
import pandas as pd

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

TWILIO_ACCOUNTSID = "ACabc7e86ae1c22592eecb70a7392c09f9"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
with open("tradingnewsalert/Vantage.bd", "r") as f:
    STOCK_APIKEY = f.readline()
with open("tradingnewsalert/NewsAPI.bd", "r") as f:
    NEWS_APIKEY = f.readline()
with open("tradingnewsalert/Twilio.bd", "r") as f:
    TWILIO_AUTHTOKEN = f.readline()
NEWS_API_KEY = "YOUR_API_KEY"

# STEP 1: Use https://newsapi.org/docs/endpoints/everything
# When STOCK price increases/decreases by 5% between yesterday and the day before yesterday, then print("Get News").
# HINT 1: Get the closing price for yesterday and the day before yesterday. Find the positive difference between the two prices. e.g., 40 - 20 = -20, but the positive difference is 20.
# HINT 2: Work out the value of 5% of yesterday's closing stock price.

# Fetch stock data
params = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": STOCK_APIKEY
}
response = requests.get(STOCK_ENDPOINT, params=params)
response.raise_for_status()
data = response.json()
data = data["Time Series (Daily)"]
stockprice = pd.DataFrame.from_dict(data, orient="index")

# Rename columns
newname = {
    "index": "Date",
    "1. open": "Open",
    "2. high": "High",
    "3. low": "Low",
    "4. close": "Close",
    "5. adjusted close": "Adj Close",
    "6. volume": "Volume",
    "7. dividend amount": "Dividend Amount",
    "8. split coefficient": "Split Coefficient"
}
stockprice.reset_index(inplace=True)
stockprice = stockprice.rename(columns=newname)


# Fetch news data
params = {
    "q": COMPANY_NAME,
    "from": dt.timedelta(days=1),
    "sortBy": "publishedAt",
    "apiKey": NEWS_APIKEY
}
response = requests.get(NEWS_ENDPOINT, params=params)
response.raise_for_status()
data = response.json()
info = pd.DataFrame(data["articles"])


# Perform analysis on stock prices
for daynumber in range(0, int(stockprice.shape[0])-3):
    yesterday = stockprice.iloc[daynumber]
    daybefore = stockprice.iloc[daynumber+1]
    dateofyesterday = dt.datetime.strptime(yesterday["Date"], "%Y-%m-%d")
    yesterday_closing_price = float(yesterday["Close"])
    daybefore_closing_price = float(daybefore["Close"])
    pricedifference = (yesterday_closing_price - daybefore_closing_price) / daybefore_closing_price * 100

    if abs(pricedifference) >= 5:
        print("Get News for : " + COMPANY_NAME + " on " + str(dateofyesterday))
        print("The price difference is : " + str(pricedifference) + "%")
        print("The closing price of yesterday was : " + str(yesterday_closing_price))
        print("The closing price of day before yesterday was : " + str(daybefore_closing_price))
        print("The news is : " + info.iloc[daynumber]["title"])
        print("The news content is :  " + info.iloc[daynumber]["content"])
        print("-----------------------------------------------------")
        # You can add code here to send a notification or perform other actions based on the news alert.


