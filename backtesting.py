import csv, datetime, copy

from main import run
from utils import load_portfolios, load_alerts

def update_portfolio(portfolios, alerts, prices, trades, fee_percent=0.15):

    pname = alerts[0]['portfolio']
    portfolio = portfolios[pname]
    #print('PORTFOLIO ANTES: ', str(portfolio))
    #print('TRADES: ', str(trades))
    for asset, operation, amount in trades:
        if operation == 'SELL':
            new_amount = float(portfolio['portfolio_assets'][asset]['amount']) - amount
            amount = amount * (100.0 - fee_percent)/100.0
            usd_amount = amount * prices[asset]
            portfolio['portfolio_assets']['usd']['amount'] = float(portfolio['portfolio_assets']['usd']['amount']) + usd_amount
            portfolio['portfolio_assets'][asset]['amount'] = str(new_amount)
        if operation == 'BUY':
            usd_amount = amount * prices[asset]
            amount = amount * (100.0 - fee_percent)/100.0
            new_amount = float(portfolio['portfolio_assets'][asset]['amount']) + amount
            portfolio['portfolio_assets']['usd']['amount'] = float(portfolio['portfolio_assets']['usd']['amount']) - usd_amount
            portfolio['portfolio_assets'][asset]['amount'] = str(new_amount)
    #print('PORTFOLIO DESPUES: ', str(portfolio))
    portfolios[pname] = portfolio
    return portfolios


def total_value(portfolio, prices):
    ret = 0.0
    for asset in prices.keys():
        ret += prices[asset] * float(portfolio['portfolio_assets'][asset]['amount'])
    return ret

def one_backtest(alerts, period, portfolios, asset1, asset2):
    asset_ticker = {
        'avalanche-2' : 'AVAX',
        'terra-luna' : 'LUNA',
        'ethereum': 'ETH',
        'bitcoin': 'BTC',
    }
    ticker1, ticker2 = asset_ticker[asset1], asset_ticker[asset2]

    initial_value = None # total_value(portfolios['volatility'])

    first_price1, first_price2 = None, None
    last_price1, last_price2 = None, None

    pname = alerts[0]['portfolio']

    nro_trades = 0
    fname1 = 'data/%sBUSD-5m-2022-Ene-Feb-Mar-FLAT-PRICE.csv' % ticker1
    fname2 = 'data/%sBUSD-5m-2022-Ene-Feb-Mar-FLAT-PRICE.csv' % ticker2
    with open(fname1, newline='') as file1:
        with open(fname2, newline='') as file2:
             spamreader1 = csv.reader(file1, delimiter=',', quotechar='|')
             spamreader2 = csv.reader(file2, delimiter=',', quotechar='|')
             i = -1
             k = 0
             for row1,row2 in zip(spamreader1,spamreader2):
                 i += 1
                 if i % period != 0:
                     continue
                 k += 1

                 if first_price1 == None:
                     first_price1, first_price2 = float(row1[1]), float(row2[1])

                 #if k > 8000:
                 #    break

                 #print (row1+row2)
                 if row1[0] != row2[0]:
                    #print('!!!!!')
                    break

                 prices = {
                     asset1 : float(row1[1]),
                     asset2: float(row2[1]),
                     'usd': 1.0
                 }
                 if i == 0:
                     initial_value = total_value(portfolios[pname], prices)

                 msg, trades = run(portfolios, alerts, prices, mail_enabled=False)
                 #print('TRADES back: ', trades)
                 if trades != []:
                     portfolios = update_portfolio(portfolios, alerts, prices, trades)
                     nro_trades += 1
                     #print('-'*80)
                     #print(str(datetime.datetime.utcfromtimestamp(int(row1[0])/1000)) + '  ' + str(row1[0]))
                     #print('TOTAL USD = ', total_value(portfolios[pname],prices))
                     #print(prices)
                     #print('#%d %s'%(nro_trades, str(trades)))
                     #print(portfolios[pname]['portfolio_assets'])

    last_price1, last_price2 = prices[asset1], prices[asset2]
    final_value = total_value(portfolios[pname], prices)
    #print('final_value = ', final_value)
    return_percent = (final_value / initial_value - 1.0) * 100.0
    print('#trades = ', nro_trades)
    print('#points = ', k)
    print('strategy return percent = %.4f' % return_percent)
    benchmark_return = (((last_price2/first_price2-1)*0.5 + (last_price1/first_price1-1)*0.5) * 0.8)*100.0
    print(last_price1, first_price1, last_price2, first_price2)
    print('base return benchmark percent = %.4f' % benchmark_return)
    print('diff with benchmark percent = %.4f' % (return_percent-benchmark_return))

    print('-'*80)
    return return_percent, nro_trades, benchmark_return


def backtest():

    period = 12 # 5m * 6 = 60m

    portfolios = load_portfolios(backtesting=True)#default_portfolio()
    portfolios_backup = copy.deepcopy(portfolios)
    alerts = load_alerts(backtesting=True)#default_alerts()
    alerts = alerts[2:]

    alerts1 = alerts[0:2]
    alerts2 = alerts[2:4]
    print(alerts1)
    print(alerts2)

    pname = 'volatility'
    asset1 = 'avalanche-2' #'bitcoin' # 'avalanche-2'
    asset2 = 'terra-luna' #'ethereum' # 'terra-luna'
    cash_percentage = 20.0

    strategy = 'CASH' # 'CRYPTOPAIR' # 'HYBRID'

    if strategy == 'HYBRID':
        curr_alerts = alerts#alerts1#alerts1
    elif strategy == 'CASH':
        curr_alerts = alerts1
    elif strategy == 'CRYPTOPAIR':
        curr_alerts = alerts2
    delta_percentage = 2.0

    best_period = None
    best_delta_percentage = None
    best_ret_percent = -1000
    best_ret_diff = -1000
    best_nro_trades = None

    # period
    rangej = [48]#[24]#[20,22,24,26,28]#[18,24,30]#[2,4,8,16,32,64,128,256] #[120,122,124,126,128,130,132,134,136]#[4,8,16,32,64,128,256] #list(range(1, 25))
    rangej.reverse()
    # delta percent
    rangei = [1.2,1.3,1.4,1.5,1.6]#[1.18,1.19,1.2,1.21,1.22]#[1.10,1.15,1.20,1.25,1.30]#[120,122,124,126,128,130,132,134,136]#[2,4,8,16,32,64,128,256] #list(range(1, 41))
    rangei.reverse()
    rangeicrypto = [7.2,7.4,7.6,7.8,8.0]  # [1.18,1.19,1.2,1.21,1.22]#[1.10,1.15,1.20,1.25,1.30]#[120,122,124,126,128,130,132,134,136]#[2,4,8,16,32,64,128,256] #list(range(1, 41))
    rangeicrypto.reverse()


    for j in rangej:
        for i, icrypto in zip(rangei,rangeicrypto):

            delta_percentage = i #* 0.05
            delta_percentage_cryptos = icrypto
            portfolios = copy.deepcopy(portfolios_backup)

            period = j
            print('backtesting period = %d delta percentage = %f delta percent pair cryptos = %f ' % (period,delta_percentage, delta_percentage_cryptos))
            portfolios[pname]['cash_percentage'] = cash_percentage
            if len(curr_alerts) == 2:
                if curr_alerts[0]['type'] == 'cash_percentage':
                    curr_alerts[0]['value'] = (100 - cash_percentage) + delta_percentage
                    curr_alerts[1]['value'] = (100 - cash_percentage) - delta_percentage
                elif curr_alerts[0]['type'] == 'crypto_percentage':
                    curr_alerts[0]['value'] = delta_percentage_cryptos
                    curr_alerts[1]['value'] = delta_percentage_cryptos
            elif len(curr_alerts) == 4:
                print('delta percentage pair cryptos = %f ' % (delta_percentage_cryptos))
                curr_alerts[0]['value'] = (100 - cash_percentage) + delta_percentage
                curr_alerts[1]['value'] = (100 - cash_percentage) - delta_percentage
                curr_alerts[2]['value'] = delta_percentage_cryptos
                curr_alerts[3]['value'] = delta_percentage_cryptos

            # portfolio x 10
            portfolios['volatility']['portfolio_assets']['usd']['amount'] = str(float(portfolios['volatility']['portfolio_assets']['usd']['amount']) * 1000)
            portfolios['volatility']['portfolio_assets'][asset1]['amount'] = str(float(portfolios['volatility']['portfolio_assets'][asset1]['amount']) * 1000)
            portfolios['volatility']['portfolio_assets'][asset2]['amount'] = str(float(portfolios['volatility']['portfolio_assets'][asset2]['amount']) * 1000)

            #print(curr_alerts)
            ret_percent, nro_trades, benchmark_percent = one_backtest(curr_alerts, period, portfolios, asset1, asset2)
            ret_diff = ret_percent - benchmark_percent
            if ret_diff > best_ret_diff:
                best_period = period
                best_delta_percentage = delta_percentage
                best_ret_percent = ret_percent
                best_nro_trades = nro_trades
                best_ret_diff = ret_diff
                print('BEST PERIOD = ', best_period)
                print('BEST DELTA PERCENT = ', best_delta_percentage)
                print('BEST # TRADES = ', best_nro_trades)
                print('BEST RETURN PERCENT = %.4f' % best_ret_percent)
                print('NEW BEST RETURN DIFF WITH BENCHMARK = %.4f' % best_ret_diff)

    print('='*80)
    print('FINAL RESULT!!!')
    print('BEST PERIOD = ', best_period)
    print('BEST DELTA PERCENT = ', best_delta_percentage)
    print('BEST # TRADES = ', best_nro_trades)
    print('BEST RETURN PERCENT = %.4f' % best_ret_percent)
    print('BEST RETURN DIFF WITH BENCHMARK = %.4f' % best_ret_diff)

if __name__ == '__main__':
    backtest()