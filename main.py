import matplotlib.pyplot as plt
import requests
import yfinance as yf
from datetime import datetime, timedelta, date


def retrieve_json(url):
    headers = {
        'User-Agent': 'YourAppName/1.0 (frishberg@uchicago.edu)'
    }
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code}")
    except requests.exceptions.JSONDecodeError as json_err:
        print(f"Error decoding JSON: {json_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None

def get_stock_price_on_date(ticker_symbol, date_str):
    date = datetime.strptime(date_str, '%m-%d-%y')
    
    for attempt in range(7):
        start_date = date - timedelta(days=attempt)
        end_date = start_date + timedelta(days=1)
        
        try:
            data = yf.download(ticker_symbol, start=start_date, end=end_date)
            if not data.empty:
                return data['Close'].iloc[0]
        except Exception as e:
            print(f"Attempt {attempt+1}: Error fetching stock price for {ticker_symbol} on {start_date.strftime('%m-%d-%Y')}: {e}")
    
    return None

def format_date(date_str):
    temp = str(int(date_str[4:6])) + "/"  + date_str[2:4]
    return temp

def get_wiki_views_data(article, num_years) :
    article = article.replace(" ", "_")
    today = date.today()
    cur_date = today.strftime("%Y%m%d")
    past_date = (today.replace(year=today.year-num_years)).strftime("%Y%m%d")
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{article}/monthly/{past_date}/{cur_date}"
    data = retrieve_json(url)
    views = []
    dates = []

    for item in data["items"] :
        views.append(item["views"])
        dates.append(format_date(item["timestamp"]))

    #removing current month because it's incomplete
    dates.remove(dates[-1])
    views.remove(views[-1])
    #removing first month because it's incomplete

    return dates, views

def plot_wiki_views(article, num_years) :
    dates, views = get_wiki_views_data(article, num_years)
    plt.plot(dates, views)
    plt.xlabel("Date")
    plt.ylabel("Views")
    plt.title(f"Monthly Views for {article.replace('_', ' ')} over the last {num_years} years")
    plt.show()

import matplotlib.pyplot as plt

def plot_wiki_views_and_stock_price(article, ticker_symbol, num_years):
    dates, views = get_wiki_views_data(article, num_years)
    stock_prices = []
    for date in dates:
        formatted_date = date[:date.index("/")] + "-28-" + date[date.index("/")+1:]
        stock_price = get_stock_price_on_date(ticker_symbol, formatted_date)
        stock_prices.append(stock_price)
        print(f"Date: {date}, Stock Price: {stock_price}")
    
    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Wikipedia Views', color=color)
    ax1.plot(dates, views, color=color, label="Wikipedia Views")
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()
    color = 'tab:green'
    ax2.set_ylabel('Stock Price', color=color)
    ax2.plot(dates, stock_prices, color=color, label="Stock Price")
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig.tight_layout()
    plt.title(f"Monthly Views and Stock Price for {article.replace('_', ' ')} over the last {num_years} years")
    fig.legend(loc="upper left", bbox_to_anchor=(0.1,0.9))
    plt.show()

plot_wiki_views_and_stock_price("Pepsi", "PEP", 1)