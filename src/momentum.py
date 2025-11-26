"""
Uses MA crossovers and RSI thresholds to produce simple trade signals.
"""

import numpy as np
import get_binance_data as gbd
import metrics as m


def apply_momentum(df, n, rsi_period=14, rsi_max=65, rsi_min=40):
    # Compute moving averages and RSI, then derive a signal column
    df = m.get_MA(df, n, 3*n)
    rsi = m.get_RSI(df, rsi_period)
    df = df.join(rsi, how='left')

    df['side_diff'] = df['fast_ma'] - df['slow_ma']
    df['side'] = df['side_diff'].apply(np.sign)

    long_signals = ((df['side'] == 1) & (df['side'].shift(1) == -1)) & (df['side'].shift(2) == -1) & (df['side'].shift(3) == -1) & (df['rsi'] >= rsi_max)
    short_signals = ((df['side'] == -1) & (df['side'].shift(1) == 1)) & (df['side'].shift(2) == 1) & (df['side'].shift(3) == 1) & (df['rsi'] <= rsi_min)

    df['signal'] = 0
    df.loc[long_signals, 'signal'] = 1
    df.loc[short_signals, 'signal'] = -1

    if df['signal'].iloc[-1] == 1:
        return True, df
    elif df['signal'].iloc[-1] == -1:
        return False, df
    else:
        return None, df
