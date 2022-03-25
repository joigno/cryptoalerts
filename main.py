# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from pycoingecko import CoinGeckoAPI
import json, datetime

from send_emails import send_email
from web_data import default_portfolio, default_alerts

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

def load_alerts():
    try:
        ret_val = default_alerts()
    except:
        ret_val = json.load(open('alerts.json'))
    return ret_val

def load_portfolios():
    try:
        ret_val = default_portfolio()
    except:
        ret_val = json.load(open('portfolio.json'))
    return ret_val


def process_alert_single(alert, prices, cg, portfolios):
    triggered = False
    asset = alert['asset_id']
    if asset not in prices:
        price = cg.get_price(ids=asset, vs_currencies='usd')[asset]['usd']
        prices[asset] = price
    else:
        price = prices[asset]
    # analyze logical conditions
    if alert['condition'] == '>':
        triggered = price > float(alert['value'])
    elif alert['condition'] == '<':
        triggered = price < float(alert['value'])
    return triggered, prices


def update_prices_portfolio(portfolio,prices, cg):
    cash_value = 0.0
    for asset in portfolio['portfolio_assets'].keys():
        if asset == 'usd':
            continue
        if asset not in prices:
            price = cg.get_price(ids=asset, vs_currencies='usd')[asset]['usd']
            prices[asset] = price
        cash_value += prices[asset] * float(portfolio['portfolio_assets'][asset]['amount'])
    return cash_value, prices


def calculate_rebalancing(cash_value, usd_total, prices, portfolio, min_trade_usd):
    """cash_value <- total usd in crypto
       usd_total <- cantidad de busd
       prices <- 
       portfolio <- el json que aparece en default.json file
       tolerance_usd <- minimum volume para operar"""
    ret = ''
    total_value = cash_value + usd_total
    print('total_value = ', total_value)
    # cash_percentage is really non-cash percentage
    cash_percentage_portfolio = float(portfolio['cash_percentage'])
    expected_value = total_value * (100.0-cash_percentage_portfolio) / 100.0
    print('expected_value = ', expected_value)
    num_assets = len(portfolio['portfolio_assets'].keys())
    balanced_value = expected_value / (num_assets-1)
    print('balanced_value = ', balanced_value)

    for asset in portfolio['portfolio_assets'].keys():
        if asset == 'usd':
            continue
        # diff
        curr_amount = float(portfolio['portfolio_assets'][asset]['amount'])
        print("amount %s = "% asset, curr_amount)
        curr_value = curr_amount * prices[asset]
        print("price %s = "% asset, prices[asset])
        diff_value = curr_value - balanced_value
        print("curr_value %s = "% asset, curr_value)
        print('diff_value %s =' % asset, diff_value)
        if diff_value > min_trade_usd:
            # SELL
            sell_amount = diff_value / prices[asset]
            ret += '<br/>\nSELL %f %s' % (sell_amount, asset.upper())
        elif diff_value < -min_trade_usd:
            # BUY
            buy_amount = -diff_value / prices[asset]
            ret += '<br/>\nBUY %f %s' % (buy_amount, asset.upper())
    return ret


def process_alert_cash(alert, prices, cg, portfolios):
    min_trade_usd = float(alert['min_trade_usd'])
    triggered = False
    portfolio_name = alert['portfolio']
    portfolio = portfolios[portfolio_name]
    # cash value of non-USD assets
    cash_value, prices = update_prices_portfolio(portfolio,prices,cg)
    print('cash_value = ', cash_value)
    # cash value of USD assets
    usd_total = float(portfolio['portfolio_assets']['usd']['amount'])
    print('usd_total = ', usd_total)
    cash_percentage_alert = float(alert['value'])
    current_cash_percentage = 100.0 * cash_value / (cash_value + usd_total)
    print('cash_percentage_alert = ',cash_percentage_alert)
    print('current_cash_percentage = ', current_cash_percentage)
    print('cash_percentage_portfolio = ', portfolio['cash_percentage'])

    # analyze logical conditions
    msg_extra = ''
    if alert['condition'] == '>':
        triggered = current_cash_percentage > cash_percentage_alert
        msg_extra = calculate_rebalancing(cash_value, usd_total, prices, portfolio, min_trade_usd)
    elif alert['condition'] == '<':
        triggered = current_cash_percentage < cash_percentage_alert
        msg_extra = calculate_rebalancing(cash_value, usd_total, prices, portfolio, min_trade_usd)
    return triggered, prices, msg_extra


def process_alert_crypto(alert, prices, cg, portfolios):
    min_trade_usd = float(alert['min_trade_usd'])
    triggered = False
    portfolio_name = alert['portfolio']
    portfolio = portfolios[portfolio_name]
    # cash value of non-USD assets
    cash_value_cryptos, prices = update_prices_portfolio(portfolio,prices,cg)
    print('cash_value_cryptos = ', cash_value_cryptos)

    msg_extra = ''
    cryptos_num = len(portfolio['portfolio_assets'].keys()) - 1
    target_crypto_percentage = (1 / cryptos_num) * 100.0
    target_crypto_value = (cash_value_cryptos / cryptos_num)

    for asset in portfolio['portfolio_assets'].keys():
        if asset == 'usd':
            continue
        print('asset = ', asset.upper())
        # cash value of 1 crypto asset
        curr_amount = float(portfolio['portfolio_assets'][asset]['amount'])
        print("amount %s = "% asset, curr_amount)
        curr_value = curr_amount * prices[asset]
        curr_crypto_percentage = 100.0 * curr_value / cash_value_cryptos

        # analyze logical conditions
        condition_value = float(alert['value'])
        print('condition ', alert['condition'])
        print('curr_crypto_percentage = ', curr_crypto_percentage)
        print('delta_condition_percentage = ', condition_value)
        print('limit_condition_percentage = ', target_crypto_percentage + condition_value)
        if alert['condition'] == '>':
            triggered = curr_crypto_percentage > target_crypto_percentage + condition_value
            portfolio['cash_percentage'] = 0
            portfolio['portfolio_assets']['usd']['amount'] = 0
            msg_extra = calculate_rebalancing(cash_value_cryptos, 0.0, prices, portfolio, min_trade_usd)

        elif alert['condition'] == '<':
            triggered = curr_crypto_percentage < target_crypto_percentage - condition_value
            portfolio['cash_percentage'] = 0
            portfolio['portfolio_assets']['usd']['amount'] = 0
            msg_extra = calculate_rebalancing(cash_value_cryptos, 0.0, prices, portfolio, min_trade_usd)

        if triggered:
            break
    return triggered, prices, msg_extra


def run(portfolios=None, alerts=None, prices=None):
    print_hi('PyCharm')
    cg = CoinGeckoAPI()
    print(cg.get_price(ids='ampleforth', vs_currencies='usd'))

    # portfolio https://raw.githubusercontent.com/joigno/alerts/main/default.json
    if not portfolios:
        portfolios = load_portfolios()
    if not alerts:
        alerts = load_alerts()
    if not prices:
        prices = {}

    msg = ''
    status_sent = {}
    for alert in alerts:
        print('--------------- processsing alert %s ---------------' % alert['type'].upper())
        if alert['type'] == 'single_asset':
            triggered, prices = process_alert_single(alert, prices, cg, portfolios)
            if triggered:
                # Send Email
                print(alert['message'])
                send_email(alert['recipient'].split(','), 'CRYPTO-ALERT: '+ alert['message'], alert['message'])

        elif alert['type'] == 'cash_percentage':
            triggered, prices, msg_extra = process_alert_cash(alert, prices, cg, portfolios)
            if triggered:
                # Send Email
                msg = alert['message'] + '<br/>\n' + msg_extra
                subject = 'ALERT crypto-alerts: ' + alert['message']
                print(msg)
                send_email(alert['recipient'].split(','), subject, msg)

        elif alert['type'] == 'crypto_percentage':
            triggered, prices, msg_extra = process_alert_crypto(alert, prices, cg, portfolios)
            if triggered:
                # Send Email
                msg = alert['message'] + '<br/>\n' + msg_extra
                subject = 'ALERT crypto-alerts: ' + alert['message']
                print(msg)
                send_email(alert['recipient'].split(','), subject, msg)

    # Send Status Message (Daily)
    if datetime.datetime.now().hour == 12:
        print('INFO: sending status email')
        subject = 'INFO crypto-alerts: system is up and running'
        msg = subject + '\n' + '<pre>' + json.dumps(portfolios, indent=4, sort_keys=True)  \
              + '\n' + json.dumps(alerts, indent=4, sort_keys=True) + '<pre/>'
        recipients = alert['recipient'].split(',')
        for recp in recipients:
            if not recp in status_sent:
                send_email(alert['recipient'].split(','), subject, msg)
            status_sent[recp] = True


    return msg

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
