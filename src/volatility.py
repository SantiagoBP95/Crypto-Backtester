"""Utility script to compute and plot returns volatility."""

import get_binance_data as gbd
import metrics as m


if __name__ == '__main__':
    df = gbd.get_binance_data()
    volatility, _ = m.get_returns_volatility(df)
    m.plot(df, volatility=volatility)
