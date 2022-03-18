import requests
import json

def default_portfolio():
    url = 'https://raw.githubusercontent.com/joigno/alerts/main/default.json'
    print(url)
    resp = requests.get(url=url, headers={'Cache-Control': 'no-cache'})
    #print(resp.text)
    #print(json.loads(resp.text))
    data = resp.json() # Check the JSON Response Content documentation below
    print(data)
    return data

def default_alerts():
    url = 'https://raw.githubusercontent.com/joigno/alerts/main/default_alerts.json'
    print(url)
    resp = requests.get(url=url, headers={'Cache-Control': 'no-cache'})
    #print(resp.text)
    #print(json.loads(resp.text))
    data = resp.json() # Check the JSON Response Content documentation below
    print(data)
    return data

if __name__ == "__main__":
    default_portfolio()