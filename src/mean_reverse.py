"""
This module computes Bollinger Bands and returns a simple entry signal
based on price interactions with the bands. The function returns a
boolean-like signal and the DataFrame of bands for plotting/inspection.
"""

import pandas as pd
import get_binance_data as gbd
import metrics as m


def apply_mean_reverse(df, n):
    # Calculate Bollinger Bands and mark potential entries
    bbands = m.get_bollinger_bands(df, window=n)

    bbands['side'] = 0
    bbands['side_ref'] = df['close'].shift(1)

    # Entry masks: detect price crossing into the band area
    long_signals = (df['close'] <= bbands['lower_band']) & (df['close'].shift(1) >= bbands['lower_band'].shift(1))
    short_signals = (df['close'] >= bbands['upper_band']) & (df['close'].shift(1) <= bbands['upper_band'].shift(1))

    bbands['signal'] = 0
    bbands.loc[long_signals, 'signal'] = 1
    bbands.loc[short_signals, 'signal'] = -1

    # Return a concise signal based on recent bars
    if bbands['signal'].iloc[-2] == 1:
        return True, bbands
    elif bbands['signal'].iloc[-2] == -1:
        return False, bbands
    else:
        return None, bbands
