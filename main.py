# _________________________________
# Libraries | Modules
# _________________________________

from binance.client import Client
from binance.enums import *
# ____
from instance.config import api_key, api_secret
import json
# ____
import matplotlib.pyplot as plt
# ____
import pandas as pd
# ____
import numpy as np
# ____
from datetime import datetime
import json

# _________________________________
# API Config
# _________________________________

# ** Binance Exchange
# client = Client(api_key, api_secret)

# _________________________________
# Global Pandas Dataframe Viewing Options
# pd.set_option('display.max_rows', 2000)
# _________________________________

def hist_candlestick():
    """
    Get Data from Target Exchange and Store set data in a JSON file
    """

    data = []

    # Historical K-Lines:
    klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 Dec, 2019", "1 Jan, 2020")

    # Real-Time K-Lines:
    # klines = client.get_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1MINUTE)

    # Assign Data Into JSON Format:
    for candle in klines:
        open_time = datetime.utcfromtimestamp(
            int(candle[0]) / 1000).strftime('%Y-%m-%d %H:%M:%S')
        close_time = datetime.utcfromtimestamp(
            int(candle[6]) / 1000).strftime('%Y-%m-%d %H:%M:%S')
        p_open = round(float(candle[1]))
        p_high = round(float(candle[2]))
        p_low = round(float(candle[3]))
        p_close = round(float(candle[4]))
        volume = round(float(candle[5]))
        quote_asset_volume = round(float(candle[7]))
        num_trades = round(float(candle[8]))
        taker_buy_base_asset_volume = round(float(candle[9]))
        taker_buy_quote_asset_volume = round(float(candle[10]))

        data.append({
                    'open_time': open_time,
                    'p_open': p_open,
                    'p_high': p_high,
                    'p_low': p_low,
                    'p_close': p_close,
                    'volume': volume,
                    'close_time': close_time,
                    'quote_asset_volume': quote_asset_volume,
                    'num_trades': num_trades,
                    'taker_buy_base_asset_volume': taker_buy_base_asset_volume,
                    'taker_buy_quote_asset_volume': taker_buy_quote_asset_volume
                    })

    # Store Data .json file:
    with open('hist_data/1_Dec_2019 - 1_Jan_2020.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        print('Data Added Sucessfully')


def get_hist_data():
    """
    Get Target Historical Candle Data from the .json file
    ---
    Return -> Pandas DataFrame (df)
    """

    # Availale Data:
    # hist_data/1_Dec_2019 - 1_Jan_2020.json

    data_json = pd.read_json('hist_data/1_Dec_2019 - 1_Jan_2020.json')
    df = pd.DataFrame(data_json)
    return df


def x2_sma_cross_strategy():
    """
    Desc:
    A function handler for x2_sma_cross strategy, located in the strategy/ folder,
    creates a final JSON file for X variable strategy input value permutation for 
    further anaylsis by the risk_management() function,

    Return:
    Output JSON file with a backtested portfolio
    """

    # A Python program to print all combinations of given length
    from itertools import combinations, permutations
    from MarketOnClosePortfolio import MarketOnClosePortfolio
    from strategy.x2_sma_cross import SMA_Cross

    risk_data = []

    # Get all permutations/combinations of [1, 2, 3] and length 2
    list_of_ints = list(range(4)) # ie: 50
    perm = permutations(list_of_ints, 2)

    # For Loop permutations/combinations:
    for i in list(perm):

        if (i[0] > 0) & (i[1] > 1):

            # Pass Strategy Parameters: [fast_window, slow_window, dataframe]
            strategy = SMA_Cross(i[0], i[1], get_hist_data())
            strategy_data = strategy.generate_signals()

            # Pass Strategy Data Parameters for Backtesting [strategy_data DataFrame]
            # portfolio = MarketOnClosePortfolio(strategy_data)
            portfolio = MarketOnClosePortfolio(initial_capital=1000.00, cap_on_order=500.00, inital_num_shares=0, comission_per_trade=0.1, symbol="BTC/USDT", data=get_hist_data(), signal_hist=strategy_data)
            returns = portfolio.backtest_portfolio_v3()

            # Risk Management:
            risk_metrics = risk_management(returns)
            risk_metrics.update({'permutation': i})
            risk_data.append(risk_metrics)

    # print(risk_data)
    # print('\n' + 'Permutation Strategy Sucessfully Backtested!' + '\n')

    with open('out2.json', 'w') as file:
        json.dump(risk_data, file, ensure_ascii=False, indent=4)
        print('Data Saved Sucessfully')


def risk_management(portfolio):
    """
    Args:
    Portfolio in the form of Pandas dataframe,

    Desc:
    Method for asessing the risk of a particular incoming strategy,

    Return:
    JSON Object with Risk Assesment for a single x,y permutation
    """

    # Risk Management Metrics:
    trading_period = portfolio['Buy Order Time'].iloc[-1] - portfolio['Buy Order Time'].iloc[0]
    total_paid_comission = portfolio['Comission ($)'].sum()
    num_closed_trades = portfolio.shape[0]
    num_win_trades = portfolio.loc[portfolio['(%) Change'] > 0.0, '(%) Change'].count()
    num_loss_trades = portfolio.loc[portfolio['(%) Change'] < 0.0, '(%) Change'].count()
    percent_profitable = (num_win_trades / num_closed_trades) * 100
    gross_profit = portfolio.loc[portfolio['(%) Change'] > 0.0, '(%) Change'].sum()
    gross_loss = portfolio.loc[portfolio['(%) Change'] < 0.0, '(%) Change'].sum()
    net_profit = gross_profit + gross_loss
    profit_factor = gross_profit / (-gross_loss)
    avg_win_trade = gross_profit / num_win_trades
    avg_loss_trade = gross_loss / num_loss_trades
    buy_and_hold_return = portfolio['Share Quantity'].iloc[0] * (portfolio['Buy Price'].iloc[-1] - portfolio['Buy Price'].iloc[0])
    sharpe_ratio = np.sqrt(252) * (portfolio['(%) Change'].mean() / portfolio['(%) Change'].std())

    risk_data_list = {
        'Trading period': str(trading_period),
        'Total Comission': str(round(total_paid_comission, 2)),
        'Qty Closed Trades': str(num_closed_trades),
        'Qty Win Trades': str(num_win_trades),
        'Qty Loss Trades': str(num_loss_trades),
        'Profitable (%)': str(percent_profitable),
        'Gross Profit': str(round(gross_profit, 4)),
        'Gross Loss': str(round(gross_loss, 4)),
        'Net Profit': str(round(net_profit, 4)),
        'Profit Factor': str(round(profit_factor, 4)),
        'Avg. Win Trade': str(avg_win_trade),
        'Avg. Loss Trade': str(avg_loss_trade),
        'Buy & Hold Return': str(round(buy_and_hold_return, 2)),
        'Sharpe Ratio': str(round(sharpe_ratio, 2))
    }

    # print('\n' + 'Strategy Risk Management Complete!' + '\n')

    return risk_data_list


def best_strategy():
    """
    Desc:
    Idenitfying the best strategy combination from a pool
    of strategy combinations,

    Retrun:
    Print the best overall strategy based on "Profitability" factor of a set strategy,
    """

    # Convert from JSON to DataFrame (df)
    data_json = pd.read_json('out.json')
    df = pd.DataFrame(data_json)

    # Filter for best strategy:
    # MOST PROFITABLE STRATEGY
    max_net_profit = df.loc[df['Profitable (%)'].idxmax()]

    print(max_net_profit)


if __name__ == '__main__':
    import time
    t0 = time.time()
    # _______________
    x2_sma_cross_strategy()
    # _______________
    best_strategy()
    # _______________
    t1 = time.time()
    print('Time to Complition: ' + str(round(t1 - t0, 5)) + ' sec.' + '\n')
