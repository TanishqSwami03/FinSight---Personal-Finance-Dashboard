import requests
import http.client
import urllib.parse
import json
from urllib.parse import quote
from decimal import Decimal
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from alpha_vantage.timeseries import TimeSeries

from .models import *

def get_top_stocks():
    url = "https://indian-stock-exchange-api2.p.rapidapi.com/NSE_most_active"
    headers = {
        "x-rapidapi-key": "047c89427dmsh4abf46c87883640p1bab6cjsnda99588c24f1",
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
        'x-rapidapi-key': "c1c626fd31msh9234c3a88568ae2p111cebjsn81b3bcc75e23",
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


ALPHA_VANTAGE_API_KEY = '9IDDAT67A3ODEWLG'

# Fetch stock data from Alpha Vantage
def fetch_stock_data(symbol):
    if not ('.BSE' in symbol or '.NS' in symbol):
        symbol += '.BSE'
    
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        raise ValueError(f"Invalid API call for {symbol}. Check your API key or symbol format.")

    time_series = data["Time Series (Daily)"]
    df = pd.DataFrame.from_dict(time_series, orient="index", dtype=float)
    df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume",
    }, inplace=True)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df

# Extract features for analysis
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def extract_features(stock_data):
    stock_data["SMA_50"] = stock_data["Close"].rolling(window=50).mean()
    stock_data["SMA_200"] = stock_data["Close"].rolling(window=200).mean()
    stock_data["RSI"] = calculate_rsi(stock_data["Close"])
    stock_data["Price Change"] = stock_data["Close"].pct_change()
    stock_data.dropna(inplace=True)
    return stock_data

# Train and save the prediction model
def train_model(stock_data):
    features = stock_data[["SMA_50", "SMA_200", "RSI", "Price Change"]]
    target = (stock_data["Close"].shift(-1) > stock_data["Close"]).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, model.predict(X_test))
    print(f"Model Accuracy: {accuracy * 100:.2f}%")

    joblib.dump(model, "trained_model.pkl")
    return model

# Predict stock action (Buy/Sell)
def predict_action(stock_symbol):
    stock_data = fetch_stock_data(stock_symbol)
    features = extract_features(stock_data)

    if not os.path.exists("trained_model.pkl"):
        train_model(features)

    model = joblib.load("trained_model.pkl")
    latest_data = features.iloc[-1][["SMA_50", "SMA_200", "RSI", "Price Change"]].values.reshape(1, -1)
    prediction = model.predict(latest_data)

    return "Buy" if prediction[0] == 1 else "Sell"

# Fetch high-potential stocks dynamically using Alpha Vantage API
def fetch_high_potential_stocks():
    # Define symbols for analysis (you can replace this with a broader list)
    stock_symbols = [
        "HDFCBANK.BSE",
        "INFY.BSE",
        "RELIANCE.BSE",
        "ICICIBANK.BSE",
        "KOTAKBANK.BSE",
        "AXISBANK.BSE",
        "ASIANPAINT.BSE",
        "TATASTEEL.BSE",
        "BAJAJFINANCE.BSE",
        "HINDUNILVR.BSE",
        "NTPC.BSE",
        "TATAMOTORS.BSE",
        "JSWSTEEL.BSE",
        "BHARTIARTL.BSE",
        "MARUTI.BSE",
        "BAJAJFINSV.BSE",
        "SUNPHARMA.BSE",
        "NESTLEIND.BSE",
        "GRASIM.BSE",
        "WIPRO.BSE",
        "DIVISLAB.BSE",
        "M&M.BSE",
        "INDUSINDBK.BSE",
        "TITAN.BSE",
        "HDFCLIFE.BSE",
        "ADANIPORTS.BSE",
        "CIPLA.BSE",
        "BAJAJ-AUTO.BSE",
        "DRREDDY.BSE",
        "EICHERMOT.BSE",
        "HINDALCO.BSE",
        "UPL.BSE",
        "SHREECEM.BSE",
        "APOLLOHOSP.BSE",
        "TECHM.BSE",
        "BPCL.BSE",
        "SBILIFE.BSE",
        "ONGC.BSE",
        "COALINDIA.BSE",
        "BRITANNIA.BSE",
        "HEROMOTOCO.BSE",
        "TATACONSUM.BSE",
    ]

    high_potential_stocks = []

    for symbol in stock_symbols:
        try:
            # Fetch stock data
            stock_data = fetch_stock_data(symbol)
            stock_data = extract_features(stock_data)

            # Analyze indicators
            latest_data = stock_data.iloc[-1]
            if latest_data["RSI"] < 30:  # Oversold condition
                high_potential_stocks.append({
                    "stock": symbol,
                    "reason": "This stock is currently oversold and may see a rebound soon. Consider buying."
                })
            elif latest_data["SMA_50"] > latest_data["SMA_200"]:  # Positive SMA crossover
                high_potential_stocks.append({
                    "stock": symbol,
                    "reason": "This stock has shown a positive trend recently, with a strong upward momentum."
                })
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    return high_potential_stocks

# Generate insights for the logged-in user
def generate_insights(user):
    portfolio = Portfolio.objects.filter(user=user)

    # Analyze user's portfolio
    suggestions = []
    for stock in portfolio:
        try:
            action, reason = predict_action(stock.stock_symbol)
        except Exception as e:
            action = "Hold"
            reason = f"Could not fetch data for {stock.stock_symbol}: {str(e)}"

        suggestions.append({
            "stock": stock.stock_symbol,
            "action": action,
            "reason": reason,
            "profit": stock.profit,
            "percentage_change": stock.percentage_change,
        })

    # Fetch high-potential stocks
    high_potential_stocks = fetch_high_potential_stocks()

    return suggestions, high_potential_stocks
