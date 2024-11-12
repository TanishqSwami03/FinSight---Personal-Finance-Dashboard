import requests

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