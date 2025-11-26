"""
Returns a pandas DataFrame with numeric OHLCV columns and a datetime index.
"""

import pandas as pd
import datetime
from binance.client import Client
import config as cfg


def get_binance_data(api_key = cfg.API_KEY, api_secret = cfg.API_SECRET, symbol=cfg.SYMBOL, interval=Client.KLINE_INTERVAL_30MINUTE, days=cfg.DAYS):
    """Download historical klines from Binance and convert them to a DataFrame.

    Args:
        api_key, api_secret: API credentials used by python-binance client.
        symbol (str): trading pair, e.g. 'BTCUSDT'.
        interval: Kline interval constant from python-binance.
        days (int): number of days to fetch.

    Returns:
        pd.DataFrame indexed by timestamp with OHLCV and derived columns.
    """
    client = Client(api_key, api_secret)
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)
    start_str = start_date.strftime("%d %b, %Y")
    end_str = end_date.strftime("%d %b, %Y")
    klines = client.get_historical_klines(symbol, interval, start_str, end_str)

    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
        'taker_buy_quote_asset_volume', 'ignore'
    ])

    df['timestamp_readable'] = pd.to_datetime(df['timestamp'], unit='ms')
    # Convert price/volume columns to numeric
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    df['quote_asset_volume'] = pd.to_numeric(df['quote_asset_volume'])
    df['number_of_trades'] = pd.to_numeric(df['number_of_trades'])
    df['taker_buy_base_asset_volume'] = pd.to_numeric(df['taker_buy_base_asset_volume'])
    df['taker_buy_quote_asset_volume'] = pd.to_numeric(df['taker_buy_quote_asset_volume'])

    df['turnover'] = df['volume'] * df['close']
    df.set_index('timestamp_readable', inplace=True)
    return df
