from main import run

import json

def test_below_percentage():
    alerts_text = '''
[
    {
    "portfolio": "volatility",
    "name": "cash-up",
    "type": "cash_percentage",
    "condition": ">",
    "value": "66.6",
    "recipient" : "joigno",
    "message" : "Cash Value of portfolio 'volatility' is above 66.6%",
      "min_trades_usd" : "10.0"
  },
    {
    "portfolio": "volatility",
    "name": "cash-down",
    "type": "cash_percentage",
    "condition": "<",
    "value": "33.3",
    "recipient" : "joigno",
    "message" : "Cash Value of portfolio 'volatility' is below 33.3%",
      "min_trades_usd" : "10.0"
  }
]
    '''
    alerts = json.loads(alerts_text)
    portfolio_text = '''
{
  "volatility": {
    "portfolio_assets": {
      "ethereum": {
        "amount": "0.4"
      },
      "bitcoin": {
        "amount": "0.01"
      },
      "usd": {
        "amount": "5784.0"
      }
    }
  }
}
    '''
    prices = {
        'bitcoin' : 41704.0,
        'ethereum' : 2935.0,
    }
    ret = '''Cash Value of portfolio 'volatility' is below 33.3%<br/>
<br/>
SELL 0.121080 ETHEREUM<br/>
BUY 0.009630 BITCOIN'''
    portfolio = json.loads(portfolio_text)
    assert run(portfolio, alerts, prices) == ret


def test_above_percentage():
    alerts_text = '''
[
    {
    "portfolio": "volatility",
    "name": "cash-up",
    "type": "cash_percentage",
    "condition": ">",
    "value": "66.6",
    "recipient" : "joigno",
    "message" : "Cash Value of portfolio 'volatility' is above 66.6%",
      "min_trades_usd" : "10.0"
  },
    {
    "portfolio": "volatility",
    "name": "cash-down",
    "type": "cash_percentage",
    "condition": "<",
    "value": "33.3",
    "recipient" : "joigno",
    "message" : "Cash Value of portfolio 'volatility' is below 33.3%",
      "min_trades_usd" : "10.0"
  }
]
    '''
    alerts = json.loads(alerts_text)
    portfolio_text = '''
{
  "volatility": {
    "portfolio_assets": {
      "ethereum": {
        "amount": "4.0"
      },
      "bitcoin": {
        "amount": "0.1"
      },
      "usd": {
        "amount": "5784.0"
      }
    }
  }
}
    '''
    prices = {
        'bitcoin' : 41704.0,
        'ethereum' : 2935.0,
    }
    ret = '''Cash Value of portfolio 'volatility' is above 66.6%<br/>
<br/>
SELL 2.359061 ETHEREUM<br/>
BUY 0.015484 BITCOIN'''
    portfolio = json.loads(portfolio_text)
    assert run(portfolio, alerts, prices) == ret


def test_good_percentage():
    alerts_text = '''
[
    {
    "portfolio": "volatility",
    "name": "cash-up",
    "type": "cash_percentage",
    "condition": ">",
    "value": "66.6",
    "recipient" : "joigno",
    "message" : "Cash Value of portfolio 'volatility' is above 66.6%",
      "min_trades_usd" : "10.0"
  },
    {
    "portfolio": "volatility",
    "name": "cash-down",
    "type": "cash_percentage",
    "condition": "<",
    "value": "33.3",
    "recipient" : "joigno",
    "message" : "Cash Value of portfolio 'volatility' is below 33.3%",
      "min_trades_usd" : "10.0"
  }
]
    '''
    alerts = json.loads(alerts_text)
    portfolio_text = '''
{
  "volatility": {
    "portfolio_assets": {
      "ethereum": {
        "amount": "1.0"
      },
      "bitcoin": {
        "amount": "0.005"
      },
      "usd": {
        "amount": "5784.0"
      }
    }
  }
}
    '''
    prices = {
        'bitcoin' : 41704.0,
        'ethereum' : 2935.0,
    }
    ret = ''''''
    portfolio = json.loads(portfolio_text)
    assert run(portfolio, alerts, prices) == ret


