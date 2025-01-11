import os
import requests
import http.client
import urllib.parse
import json
from urllib.parse import quote
from decimal import Decimal
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from datetime import datetime
from .models import *

def get_top_stocks():
    url = "https://indian-stock-exchange-api2.p.rapidapi.com/NSE_most_active"
    headers = {
        "x-rapidapi-key": "06ce2c117emshb10dee7b44d4c4ep11e44cjsn2a53a7965b9f",
        "x-rapidapi-host": "indian-stock-exchange-api2.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # return data[:5]  # Return only the top 5 stocks
        return data
    else:
        print(f"Error fetching data: {response.status_code}")
        return []


def get_stock_data(symbol):
    """
    Fetch stock data for a given symbol using the RapidAPI Indian Stock Exchange API.

    Args:
        symbol (str): The stock symbol to fetch data for.

    Returns:
        dict: A dictionary containing the stock data, including company name, 
              current price on NSE, and exchange codes for NSE and BSE.
        None: If there was an error during the API request or if no data was found.
    """
    if not symbol:
        print("Stock symbol is required!")
        return None

    # Encode the symbol to handle special characters
    encoded_symbol = quote(symbol.encode('utf-8'))  

    # API connection setup
    conn = http.client.HTTPSConnection("indian-stock-exchange-api2.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "06ce2c117emshb10dee7b44d4c4ep11e44cjsn2a53a7965b9f",
        'x-rapidapi-host': "indian-stock-exchange-api2.p.rapidapi.com"
    }

    try:
        # Make the API request
        conn.request("GET", f"/stock?name={encoded_symbol}", headers=headers)
        res = conn.getresponse()
        data = res.read()

        # Parse and validate the response
        stock_data = json.loads(data.decode("utf-8"))
        if not stock_data:
            print("No stock data found for the symbol.")
            return None

        # Extract required fields safely
        company_name = stock_data.get("companyName", "N/A")
        current_price_nse = stock_data.get("currentPrice", {}).get("NSE", None)
        exchange_code_nse = stock_data.get("companyProfile", {}).get("exchangeCodeNse", "N/A")
        exchange_code_bse = stock_data.get("companyProfile", {}).get("exchangeCodeBse", "N/A")

        # Return structured stock data
        return {
            "symbol": exchange_code_nse or symbol,  # Use provided symbol as fallback
            "company_name": company_name,
            "current_price_nse": current_price_nse,
            "exchange_code_nse": exchange_code_nse,
            "exchange_code_bse": exchange_code_bse,
        }

    except json.JSONDecodeError:
        print("Error decoding the JSON response. Ensure the API response format is correct.")
        return None
    except http.client.HTTPException as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    finally:
        conn.close()


# Insights page

def get_stock_news(stock_symbol):
    """
    Fetch recent news specifically related to a stock symbol using NewsAPI.

    Args:
        stock_symbol (str): Stock symbol to fetch news for.

    Returns:
        list: A list of up to 5 news articles containing title, description, and URL.
    """
    api_key = "d9cae1602f114f34a7575c813314e7d7"
    base_url = "https://newsapi.org/v2/everything"

    # Add specific financial terms to focus on stock-related news
    query = f"{stock_symbol} stock OR share price OR market"

    # Query parameters
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "language": "en",
        "apiKey": api_key,
        "pageSize": 5,  # Limit the results to 5 articles
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses
        news_data = response.json()

        # Extract relevant news articles
        articles = news_data.get("articles", [])
        return [
            {
                "title": article["title"],
                "description": article["description"],
                "url": article["url"],
                "source": article["source"]["name"],
                "published_at": datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d-%m-%Y, %I:%M %p"),
            }
            for article in articles
        ]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {stock_symbol}: {e}")
        return []
