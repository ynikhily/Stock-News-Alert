import requests
import datetime
from twilio.rest import Client

# GENERATE YOUR AUTH TOKEN AND ACCOUNT SID AFTER SETTING UP YOUR TWILIO ACCOUNT ON https://www.twilio.com/
account_sid = ""
auth_token = ""


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

# CREATE A FREE ACCOUNT ON https://www.alphavantage.co/ AND GET YOUR OWN ACCESS KEY TO USE.
STOCK_ACCESS_KEY = ""

# CREATE A FREE ACCOUNT ON https://newsapi.org/ TO GET AN ACCESS KEY FOR FETCHING NEWS ARTICLES.
NEWS_ACCESS_KEY = ""
function = "TIME_SERIES_DAILY"

stock_api_endpoint_url = "https://www.alphavantage.co/query"
news_api_endpoint_url = "https://newsapi.org/v2/everything"

news_parameters = {
    'qInTitle': COMPANY_NAME,
    'apiKey': NEWS_ACCESS_KEY
}

stock_parameters = {
    'function': function,
    'symbol': STOCK,
    'apikey': STOCK_ACCESS_KEY
}
# -----------------------------------------GETTING STOCK DATA---------------------------------------------
response = requests.get(stock_api_endpoint_url, stock_parameters)
response.raise_for_status()
stock_data = response.json()['Time Series (Daily)']

today = datetime.datetime.now().date()
one_day_length = datetime.timedelta(days=1)

yesterday = today - one_day_length
closing_stock_yesterday = float(stock_data[str(yesterday)]['4. close'])

day_before_yesterday = yesterday - one_day_length
closing_stock_day_before = float(stock_data[str(day_before_yesterday)]['4. close'])

stock_diff_per = abs(closing_stock_day_before-closing_stock_yesterday)*100/closing_stock_day_before

# ------------------------------ SETTING UP CONDITION ON STOCK DIFFERENCE-------------------------------------
if stock_diff_per > 1:
    news_response = requests.get(news_api_endpoint_url, news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()['articles']
    sliced_news = news_data[:3]

    if closing_stock_yesterday > closing_stock_day_before:
        stock_string = f"{STOCK}: {stock_diff_per}% 🔺"
    else:
        stock_string = f"{STOCK}: {stock_diff_per}% 🔻"

    formatted_news = [f"{stock_string}\nHeadline: {article['title']}\nBrief: {article['description']}"
                      for article in sliced_news]

# -----------------------SETTING UP A TWILIO CONNECTION AND SENDING UPDATES-------------------------------
    client = Client(account_sid, auth_token)

    for article in formatted_news:
        message = client.messages \
            .create(
            body=article,
            from_='',  # YOUR TWILIO ACCOUNT NUMBER
            to=''  # YOUR PERSONAL PHONE NUMBER WHERE YOU WANT TO RECEIVE YOUR UPDATES
        )
        print(message.status)


# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
