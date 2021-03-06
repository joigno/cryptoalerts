import requests
import logging
logging.basicConfig(filename='cryptoalerts.log', level=logging.INFO)


def default_portfolio():
    url = 'https://raw.githubusercontent.com/joigno/alerts/main/default.json'
    logging.info(url)
    resp = requests.get(url=url, headers={'Cache-Control': 'no-cache'})
    #print(resp.text)
    #print(json.loads(resp.text))
    data = resp.json() # Check the JSON Response Content documentation below
    logging.info(data)
    return data

def default_alerts():
    url = 'https://raw.githubusercontent.com/joigno/alerts/main/default_alerts.json'
    logging.info(url)
    resp = requests.get(url=url, headers={'Cache-Control': 'no-cache'})
    #print(resp.text)
    #print(json.loads(resp.text))
    data = resp.json() # Check the JSON Response Content documentation below
    logging.info(data)
    return data

if __name__ == "__main__":
    default_portfolio()