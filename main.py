# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from pycoingecko import CoinGeckoAPI
import json, datetime, logging, datetime, os

logging.basicConfig(filename='cryptoalerts.log', level=logging.INFO)

from send_emails import send_email
from utils import load_alerts, load_portfolios

cg = CoinGeckoAPI()

def get_price_market(base_ticker, target_ticker='BUSD', market='binance'):
    pairs = [ticker for ticker in cg.get_exchanges_by_id(market)['tickers']
            if ticker['base'] == base_ticker and ticker['target']==target_ticker]
    if pairs == []:
        target_ticker = 'USDT'
        pairs = [ticker for ticker in cg.get_exchanges_by_id(market)['tickers']
                if ticker['base'] == base_ticker and ticker['target']==target_ticker]
    return pairs[0]['last']


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
    asset_ticker = {
        'avalanche-2' : 'AVAX',
        'terra-luna' : 'LUNA',
        'ethereum': 'ETH',
        'bitcoin': 'BTC',
    }
    cash_value = 0.0
    for asset in portfolio['portfolio_assets'].keys():
        if asset == 'usd':
            continue
        if asset not in prices:
            #price = cg.get_price(ids=asset, vs_currencies='usd')[asset]['usd']
            price = get_price_market(asset_ticker[asset])
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
    logging.info('total_value = %.4f' % total_value)
    # cash_percentage is really non-cash percentage
    cash_percentage_portfolio = float(portfolio['cash_percentage'])
    expected_value = total_value * (100.0-cash_percentage_portfolio) / 100.0
    logging.info('expected_value = %.4f' % expected_value)
    num_assets = len(portfolio['portfolio_assets'].keys())
    balanced_value = expected_value / (num_assets-1)
    logging.info('balanced_value = %.4f'% balanced_value)

    trades = []
    for asset in portfolio['portfolio_assets'].keys():
        if asset == 'usd':
            continue
        # diff
        curr_amount = float(portfolio['portfolio_assets'][asset]['amount'])
        logging.info("amount %s = %.4f"% (asset, curr_amount))
        curr_value = curr_amount * prices[asset]
        logging.info("price %s = %.4f"% (asset, prices[asset]))
        diff_value = curr_value - balanced_value
        logging.info("curr_value %s = %.4f"% (asset, curr_value))
        logging.info("diff_value %s = %.4f"% (asset, diff_value))
        if diff_value > min_trade_usd:
            # SELL
            sell_amount = diff_value / prices[asset]
            ret += '<br/>\nSELL %f %s' % (sell_amount, asset.upper())
            trades.append((asset,'SELL',sell_amount))
        elif diff_value < -min_trade_usd:
            # BUY
            buy_amount = -diff_value / prices[asset]
            ret += '<br/>\nBUY %f %s' % (buy_amount, asset.upper())
            trades.append((asset, 'BUY', buy_amount))
    return ret, trades


def process_alert_cash(alert, prices, cg, portfolios):
    trades = []
    min_trade_usd = float(alert['min_trade_usd'])
    triggered = False
    portfolio_name = alert['portfolio']
    portfolio = portfolios[portfolio_name]
    # cash value of non-USD assets
    cash_value, prices = update_prices_portfolio(portfolio,prices,cg)
    logging.info("cash_value = %.4f" % cash_value)
    # cash value of USD assets
    usd_total = float(portfolio['portfolio_assets']['usd']['amount'])
    logging.info("usd_total = %.4f" % usd_total)
    cash_percentage_alert = float(alert['value'])
    current_cash_percentage = 100.0 * cash_value / (cash_value + usd_total)
    logging.info("cash_percentage_alert = %.4f" % cash_percentage_alert)
    logging.info("current_cash_percentage = %.4f" % current_cash_percentage)
    #print("current_cash_percentage = %.4f" % current_cash_percentage)
    logging.info("cash_percentage_portfolio = %.4f" % float(portfolio['cash_percentage']))

    # analyze logical conditions
    msg_extra = ''
    if alert['condition'] == '>':
        triggered = current_cash_percentage > cash_percentage_alert
        if triggered:
            #print("current_cash_percentage = %.4f" % current_cash_percentage)
            #print("cash_percentage_alert = %.4f" % cash_percentage_alert)
            msg_extra, trades = calculate_rebalancing(cash_value, usd_total, prices, portfolio, min_trade_usd)
            #print('TRADES CASH: ', trades)
    elif alert['condition'] == '<':
        triggered = current_cash_percentage < cash_percentage_alert
        if triggered:
            #print("current_cash_percentage = %.4f" % current_cash_percentage)
            #print("cash_percentage_alert = %.4f" % cash_percentage_alert)
            msg_extra, trades = calculate_rebalancing(cash_value, usd_total, prices, portfolio, min_trade_usd)
            #print('TRADES CASH: ', trades)
    return triggered, prices, msg_extra, trades


def process_alert_crypto(alert, prices, cg, portfolios):
    min_trade_usd = float(alert['min_trade_usd'])
    triggered = False
    trades = []
    portfolio_name = alert['portfolio']
    portfolio = portfolios[portfolio_name]
    # cash value of non-USD assets
    cash_value_cryptos, prices = update_prices_portfolio(portfolio,prices,cg)
    logging.info("cash_value_cryptos = %.4f" % cash_value_cryptos)

    msg_extra = ''
    cryptos_num = len(portfolio['portfolio_assets'].keys()) - 1
    target_crypto_percentage = (1 / cryptos_num) * 100.0
    target_crypto_value = (cash_value_cryptos / cryptos_num)

    for asset in portfolio['portfolio_assets'].keys():
        if asset == 'usd':
            continue
        logging.info("asset = %s" % asset)
        # cash value of 1 crypto asset
        curr_amount = float(portfolio['portfolio_assets'][asset]['amount'])
        logging.info("amount %s = %.4f"% (asset, curr_amount))
        curr_value = curr_amount * prices[asset]
        curr_crypto_percentage = 100.0 * curr_value / cash_value_cryptos

        # analyze logical conditions
        condition_value = float(alert['value'])
        logging.info("condition %s"% (alert['condition']))
        logging.info("curr_crypto_percentage = %.4f" % curr_crypto_percentage)
        logging.info("delta_condition_percentage = %.4f" % condition_value)
        if alert['condition'] == '>':
            triggered = curr_crypto_percentage > target_crypto_percentage + condition_value
            if triggered:
                #print("curr_crypto_percentage = %.4f" % curr_crypto_percentage)
                #print("delta_condition_percentage = %.4f" % condition_value)
                #print("target_crypto_percentage = %.4f" % target_crypto_percentage)
                logging.info("limit_condition_percentage = %.4f" % (target_crypto_percentage + condition_value))
                cash_backup = portfolio['cash_percentage']
                usd_amount_backup = portfolio['portfolio_assets']['usd']['amount']
                portfolio['cash_percentage'] = 0
                portfolio['portfolio_assets']['usd']['amount'] = 0
                msg_extra, trades = calculate_rebalancing(cash_value_cryptos, 0.0, prices, portfolio, min_trade_usd)
                portfolio['cash_percentage'] = cash_backup
                portfolio['portfolio_assets']['usd']['amount'] = usd_amount_backup

        elif alert['condition'] == '<':
            triggered = curr_crypto_percentage < target_crypto_percentage - condition_value
            if triggered:
                #print("curr_crypto_percentage = %.4f" % curr_crypto_percentage)
                #print("delta_condition_percentage = %.4f" % condition_value)
                #print("target_crypto_percentage = %.4f" % target_crypto_percentage)
                logging.info("limit_condition_percentage = %.4f" % (target_crypto_percentage - condition_value))
                cash_backup = portfolio['cash_percentage']
                usd_amount_backup = portfolio['portfolio_assets']['usd']['amount']
                portfolio['cash_percentage'] = 0
                portfolio['portfolio_assets']['usd']['amount'] = 0
                msg_extra, trades = calculate_rebalancing(cash_value_cryptos, 0.0, prices, portfolio, min_trade_usd)
                portfolio['cash_percentage'] = cash_backup
                portfolio['portfolio_assets']['usd']['amount'] = usd_amount_backup

        if triggered:
            break
    return triggered, prices, msg_extra, trades


def run(portfolios=None, alerts=None, prices=None, mail_enabled=True):
    ret_trades = []

    logging.info('='*80)
    logging.info('='*80)
    logging.info('='*80)
    logging.info('BUENOS_AIRES ' + str(datetime.datetime.now()-datetime.timedelta(hours=3)))
    logging.info('GMT (SERVER) ' + str(datetime.datetime.now()+datetime.timedelta(hours=0)))
    logging.info('PARIS        ' + str(datetime.datetime.now()+datetime.timedelta(hours=1)))

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
        logging.info('--------------- processsing alert %s ---------------' % alert['type'].upper())
        if alert['type'] == 'single_asset':
            triggered, prices = process_alert_single(alert, prices, cg, portfolios)
            if triggered:
                # Send Email
                logging.info(alert['message'])
                if mail_enabled:
                    send_email(alert['recipient'].split(','), 'CRYPTO-ALERT: '+ alert['message'], alert['message'])

        elif alert['type'] == 'cash_percentage':
            triggered, prices, msg_extra, trades = process_alert_cash(alert, prices, cg, portfolios)
            if triggered:
                # Send Email
                msg = alert['message'] + '<br/>\n' + msg_extra
                subject = 'ALERT crypto-alerts: ' + alert['message']
                logging.info(msg)
                os.system('tail -n 117 cryptoalerts.log > extra.log;')
                extra = '\n' + '<br/><pre>' + open('extra.log').read() + '<pre/>'
                if mail_enabled:
                    send_email(alert['recipient'].split(','), subject, msg + '\n\n' + extra)
                if trades != []:
                    ret_trades = trades

        elif alert['type'] == 'crypto_percentage':
            triggered, prices, msg_extra, trades = process_alert_crypto(alert, prices, cg, portfolios)
            if triggered:
                # Send Email
                msg = alert['message'] + '<br/>\n' + msg_extra
                subject = 'ALERT crypto-alerts: ' + alert['message']
                logging.info(msg)
                os.system('tail -n 117 cryptoalerts.log > extra.log;')
                extra = '\n' + '<br/><pre>' + str(open('extra.log').read()) + '<pre/>'
                if mail_enabled:
                    send_email(alert['recipient'].split(','), subject, msg + '\n\n' + extra)
                if trades != []:
                    ret_trades = trades

    # Send Status Message (Daily)
    if datetime.datetime.now().hour in [12,13,14,15]:
        logging.info('INFO: sending status email')
        subject = 'INFO crypto-alerts: system is up and running'
        msg = subject + '\n' + '<pre>' + json.dumps(portfolios, indent=4, sort_keys=True)  \
              + '\n' + json.dumps(alerts, indent=4, sort_keys=True) + '<pre/>'
        recipients = alert['recipient'].split(',')
        for recp in recipients:
            if not recp in status_sent:
                send_email(alert['recipient'].split(','), subject, msg)
            status_sent[recp] = True

    return msg, ret_trades

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

