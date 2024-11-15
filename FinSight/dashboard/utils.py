import requests
import http.client
import urllib.parse
import json
from urllib.parse import quote

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
    # URL-encode the stock name to handle spaces and special characters
    encoded_symbol = quote(symbol)

    # Initialize connection
    conn = http.client.HTTPSConnection("indian-stock-exchange-api2.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "06ce2c117emshb10dee7b44d4c4ep11e44cjsn2a53a7965b9f",  # Your API Key
        'x-rapidapi-host': "indian-stock-exchange-api2.p.rapidapi.com"
    }

    # Send GET request to the API with the properly URL-encoded stock name
    conn.request("GET", f"/historical_data?stock_name={encoded_symbol}&period=1m&filter=price", headers=headers)
    
    res = conn.getresponse()
    data = res.read()

    # Log the entire API response for debugging
    # print("API Response:", data.decode("utf-8"))

    # Parse the JSON response
    stock_data = json.loads(data.decode("utf-8"))

    # Check if stock data is available and return the most recent price
    if stock_data and "datasets" in stock_data:
        # Extract the most recent price from the "values" array under "Price"
        values = stock_data["datasets"][0]["values"]
        if values:
            return values[-1][1]  # Return the most recent price (last entry in values)
    return None