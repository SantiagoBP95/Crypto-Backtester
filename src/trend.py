"""Small utility script to visualize linear trend on price series.

This script is mainly provided as a quick demo for the `get_trend` helper
in `metrics.py` and can be executed directly for visualization.
"""

import get_binance_data as gbd
import metrics as m


if __name__ == '__main__':
    df = gbd.get_binance_data()
    trend = m.get_trend(df)
    m.plot(df, trend=trend)
