import json

from web_data import default_portfolio, default_alerts

portfolio_str = '''{
  "volatility": {
    "cash_percentage" : "20.0",
    "portfolio_assets": {
      "avalanche-2": {
        "amount": "8.72552000"
      },
      "terra-luna": {
        "amount": "8.16167000"
      },
      "usd": {
        "amount": "419.19085300"
      }
    }
  }
}'''

alerts_srt = '''[
  {
    "name": "ampl-down",
    "type": "single_asset",
    "asset_id" : "ampleforth",
    "condition": "<",
    "value": "0.95",
    "recipient" : "joigno",
    "message" : "AMPL is below 0.95 USD"
  },
  {
    "name": "ampl-up",
    "type": "single_asset",
    "asset_id" : "ampleforth",
    "condition": ">",
    "value": "1.21",
    "recipient" : "joigno",
    "message" : "AMPL is above 1.21 USD"
  },

    {
    "portfolio": "volatility",
    "name": "cash-up",
    "type": "cash_percentage",
    "condition": ">",
    "value": "80.5",
    "recipient" : "joigno,fede.carra",
    "message" : "Cash Value of portfolio 'volatility' is above 80.5%",
      "min_trade_usd": "10"
  },
    {
    "portfolio": "volatility",
    "name": "cash-down",
    "type": "cash_percentage",
    "condition": "<",
    "value": "79.5",
    "recipient" : "joigno,fede.carra",
    "message" : "Cash Value of portfolio 'volatility' is below 79.5%",
      "min_trade_usd": "10"
  },
      {
    "portfolio": "volatility",
    "name": "crypto-down",
    "type": "crypto_percentage",
    "condition": "<",
    "value": "2",
    "recipient" : "joigno,fede.carra",
    "message" : "Value of Crypto Portfolio 'volatility' is down 2.0% for some crypto",
      "min_trade_usd" : "10"
  },
      {
    "portfolio": "volatility",
    "name": "crypto-up",
    "type": "crypto_percentage",
    "condition": ">",
    "value": "2",
    "recipient" : "joigno,fede.carra",
    "message" : "Value of Crypto Portfolio 'volatility' is up 2.0% for some crypto",
      "min_trade_usd" : "10"
  }
]'''

def load_alerts(backtesting=False):
    if backtesting:
        return json.loads(alerts_srt)

    try:
        ret_val = default_alerts()
    except:
        print('LOCAL alerts.json')
        ret_val = json.load(open('alerts.json'))
    return ret_val


def load_portfolios(backtesting=False):
    if backtesting:
        return json.loads(portfolio_str)

    try:
        ret_val = default_portfolio()
    except:
        print('LOCAL portfolio.json')
        ret_val = json.load(open('portfolio.json'))
    return ret_val

