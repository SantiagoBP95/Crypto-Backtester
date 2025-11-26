"""
This module provides a lightweight backtesting flow used by the demo
runner. It intentionally keeps execution semantics simple: sequential
processing of signals, fixed contract size and no slippage/commissions.
"""

import time
import get_binance_data as gbd
import mean_reverse as mr
import momentum as mom
import metrics as m
import config as cfg
import pandas as pd


def obtener_datos(estrategia='mean_reverse'):
    """Fetch data and prepare a DataFrame suitable for the selected strategy.

    Returns the DataFrame that contains price and indicator columns used
    by the backtest functions.
    """
    data = gbd.get_binance_data()
    if estrategia == 'mean_reverse':
        signal, bbands = mr.apply_mean_reverse(data, 20)
        data = pd.concat([data['close'], bbands], axis=1)
        m.plot(data, bollinger_bands=True)
    elif estrategia == 'momentum':
        signal, df = mom.apply_momentum(data, 20)
        m.plot(df, moving_averages=True, rsi=df[['rsi']])
        data = df
    else:
        raise ValueError("Unknown strategy. Use 'mean_reverse' or 'momentum'.")
    return data


def ejecutar_backtest(data):
    """Simulate trades given a DataFrame with a 'signal' column.

    The function returns a DataFrame with one row per processed bar and
    simple bookkeeping columns like positions and order_value.
    """
    backtest = []
    n_contracts = 10
    f_tick = 'USD'
    tick = 'BTC'
    initial_position = 0

    for idx, row in data.iterrows():
        precio = row['close']
        direction = row.get('signal', 0)
        if direction == 0:
            order_value = 0
            backtest.append([initial_position, precio, direction, order_value])
            continue
        elif direction == 1:
            order_value = n_contracts * precio
            initial_position = initial_position + n_contracts
            backtest.append([initial_position, precio, direction, order_value])
            time.sleep(0.01)
        elif direction == -1:
            order_value = n_contracts * precio
            initial_position = initial_position - n_contracts
            backtest.append([initial_position, precio, direction, order_value])
            time.sleep(0.01)

    backtest_df = pd.DataFrame(backtest, columns=['positions', 'close', 'direction', 'order_value'])
    return backtest_df


def calcular_precio_promedio(backtest_df):
    """Estimate the average entry price per position change.

    This simple routine tracks the average entry price across incremental
    position changes and stores it in the returned DataFrame as 'avg_price'.
    """
    avg_price_list = []
    avg_price = 0
    for idx, row in backtest_df.iterrows():
        if row['direction'] != 0 and row['positions'] != 0:
            if avg_price == 0:
                avg_price = row['close']
                avg_price_list.append(avg_price)
            else:
                total_size = row['positions']
                first_size = backtest_df['positions'].iloc[idx - 1]
                if abs(total_size) > abs(first_size):
                    first_weight = abs(first_size) / abs(total_size)
                    last_weight = 1 - first_weight
                    first_price = first_weight * avg_price
                    last_price = last_weight * backtest_df['close'].iloc[idx]
                    avg_price = first_price + last_price
                    avg_price_list.append(avg_price)
                else:
                    avg_price_list.append(avg_price)
        elif row['direction'] != 0 and row['positions'] == 0:
            avg_price_list.append(0)
        elif row['direction'] == 0 and row['positions'] == 0:
            avg_price_list.append(0)
        else:
            avg_price_list.append(avg_price)

    backtest_df['avg_price'] = avg_price_list
    return backtest_df


def get_profit(row):
    """Compute a per-row profit percentage based on avg_price and close."""
    if row['positions'] < 0:
        percent = row['avg_price'] / row['close']
        profit_percent = (1 - percent) * (-1)
        return profit_percent
    elif row['positions'] > 0:
        percent = row['close'] / row['avg_price']
        profit_percent = (1 - percent)
        return profit_percent
    else:
        return 0


def construir_curva_rentabilidad(backtest_df):
    """Compute returns and cumulative returns for the backtest DataFrame."""
    backtest_df['returns'] = backtest_df.apply(lambda row: get_profit(row), axis=1)
    backtest_df['returns_pct'] = backtest_df['returns'] * 100
    backtest_df['cumulative_returns'] = backtest_df['returns'].cumsum()
    backtest_df['cumulative_returns_pct'] = backtest_df['cumulative_returns'] * 100
    return backtest_df


def graficar_rentabilidad(backtest_df):
    """Plot cumulative returns using matplotlib (simple visualization)."""
    import matplotlib.pyplot as plt
    plt.plot(backtest_df['cumulative_returns_pct'])
    plt.xlabel('Trades')
    plt.ylabel('Cumulative Returns (%)')
    plt.title('Cumulative Returns Over Time')
    plt.show()
