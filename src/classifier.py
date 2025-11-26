"""Simple classifier training helper for the reorganized package.

Provides a convenience function `train_and_save_model` that prepares
features, trains a RandomForest and saves it using joblib. This module
is intended for demo and educational purposes.
"""

import pandas as pd
import numpy as np
import joblib
import get_binance_data as gbd
import metrics as m


def train_and_save_model(filename='clasificador_binario.joblib'):
    """Train a RandomForest on Bollinger/Momentum features and save it.

    Args:
        filename (str): path where the model will be persisted.

    Returns:
        trained sklearn estimator
    """
    data = gbd.get_binance_data(days=365)
    b_bands = m.get_bollinger_bands(data, 20)
    df = pd.concat([data, b_bands], axis=1)
    df = m.get_MA(df, 20, 40)
    rsi = m.get_RSI(df, 20)
    df = pd.concat([df, rsi], axis=1)

    df = df[['close', 'upper_band', 'lower_band', 'fast_ma', 'slow_ma', 'rsi']]
    df['side'] = np.nan

    long_signals = (df['close'] < df['lower_band'])
    short_signals = (df['close'] > df['upper_band'])

    df.loc[long_signals, 'side'] = 1
    df.loc[short_signals, 'side'] = -1
    df['side'] = df['side'].shift(1)
    df = df.dropna()

    train_cols = ['close', 'upper_band', 'lower_band', 'fast_ma', 'slow_ma', 'rsi']
    split_n = int(0.7 * len(df))
    X_train = df[train_cols].iloc[:split_n]
    y_train = df['side'].iloc[:split_n]

    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    joblib.dump(model, filename)
    return model


if __name__ == '__main__':
    train_and_save_model()
