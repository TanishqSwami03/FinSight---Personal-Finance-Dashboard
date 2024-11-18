import requests
import http.client
import urllib.parse
import json
from urllib.parse import quote

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
    # print(f"Fetching stock data for: {symbol}")  # Debugging
    encoded_symbol = quote(symbol)

    conn = http.client.HTTPSConnection("indian-stock-exchange-api2.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "047c89427dmsh4abf46c87883640p1bab6cjsnda99588c24f1",
        'x-rapidapi-host': "indian-stock-exchange-api2.p.rapidapi.com"
    }

    try:
        conn.request("GET", f"/historical_data?stock_name={encoded_symbol}&period=1m&filter=price", headers=headers)
        res = conn.getresponse()
        # print(f"API Response Status: {res.status}")  # Debugging

        data = res.read()
        stock_data = json.loads(data.decode("utf-8"))
        # print(f"API Data: {stock_data}")  # Debugging

        if stock_data and "datasets" in stock_data:
            values = stock_data["datasets"][0]["values"]
            if values:
                return values[-1][1]  # Return the most recent price
            else:
                print("No stock values available.")
        else:
            print("Stock data or datasets not found.")
    except Exception as e:
        print(f"Error during API request: {e}")
    return None
