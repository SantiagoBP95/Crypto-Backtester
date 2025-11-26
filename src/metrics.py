""" 
Helpers for computing indicators (MA, RSI, Bollinger Bands) and for plotting
results using Plotly. Functions are intended for exploratory analysis
and visualization in the demo.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from pathlib import Path


def calculate_mean_return(df):
    df = df.copy()
    df['return'] = df['close'].pct_change()
    return df['return'].mean()


def calculate_volatility(df):
    df = df.copy()
    df['return'] = df['close'].pct_change()
    return df['return'].std()


def calculate_sharpe_ratio(df, risk_free_rate=0.01):
    mean_return = calculate_mean_return(df)
    volatility = calculate_volatility(df)
    return (mean_return - risk_free_rate) / volatility


def calculate_max_drawdown(df):
    df = df.copy()
    df['cumulative_return'] = (1 + df['close'].pct_change()).cumprod()
    df['cumulative_max'] = df['cumulative_return'].cummax()
    df['drawdown'] = df['cumulative_return'] / df['cumulative_max'] - 1
    return df['drawdown'].min()


def get_returns(df):
    df = df.copy()
    df['returns'] = np.log(df['close']).diff()
    return df['returns']


def get_returns_volatility(df, window=252):
    volatility = df.copy()
    volatility['returns'] = get_returns(df)
    volatility['volatility'] = volatility['returns'].rolling(window=window).std() * np.sqrt(window)
    vol = volatility['returns'].std() * np.sqrt(window)
    return volatility, vol


def get_bollinger_bands(df, window=20, num_std_dev=2):
    df = df.copy()
    df['mean'] = df['close'].rolling(window=window).mean()
    df['std_dev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['mean'] + (df['std_dev'] * num_std_dev)
    df['lower_band'] = df['mean'] - (df['std_dev'] * num_std_dev)
    return df[['mean', 'upper_band', 'lower_band']]


def get_MA(data, n1, n2):
    data['fast_ma'] = data['close'].rolling(window=n1).mean()
    data['slow_ma'] = data['close'].rolling(window=n2).mean()
    return data


def get_RSI(data, n):
    delta = data['close'].diff(1).dropna()

    up_chg = 0 * delta
    down_chg = 0 * delta

    up_chg[delta > 0] = delta[delta > 0]
    down_chg[delta < 0] = -delta[delta < 0]

    up_chg_avg = up_chg.ewm(com=n - 1, min_periods=n).mean()
    down_chg_avg = down_chg.ewm(com=n - 1, min_periods=n).mean()

    rs = abs(up_chg_avg / down_chg_avg)
    rsi = 100 - 100 / (1 + rs)

    rsi = rsi.dropna()
    rsi_df = pd.DataFrame({'date': data.index[-len(rsi):], 'rsi': rsi.values})
    rsi_df.set_index('date', inplace=True)
    return rsi_df


def get_trend(df):
    trend = pd.DataFrame({'close': df['close']})
    x = np.array(range(len(trend))).reshape(-1, 1)
    y = trend['close'].values.reshape(-1, 1)
    model = LinearRegression()
    model.fit(x, y)
    trend['y_predict'] = model.predict(x)
    trend['trend'] = {'slope': model.coef_[0][0], 'intercept': model.intercept_[0]}
    trend['x'] = x
    trend['y'] = y
    trend['r_2'] = model.score(x, y)
    return trend


def plot(df, bollinger_bands=False, moving_averages=False, rsi=None, volatility=None, trend=None, save_path=None, show=True):
    rows = 1
    subplot_titles = ['Precio de Cierre']
    row_heights = [0.7]

    if rsi is not None:
        rows += 1
        subplot_titles.append('RSI')
        row_heights.append(0.3)

    if volatility is not None:
        rows += 1
        subplot_titles.append('Volatilidad')
        row_heights.append(0.3)

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, subplot_titles=subplot_titles,
                        row_heights=row_heights)

    fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Precio de Cierre', line=dict(color='blue')), row=1, col=1)

    if bollinger_bands:
        fig.add_trace(go.Scatter(x=df.index, y=df['mean'], mode='lines', name='Media Móvil', line=dict(color='orange')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['upper_band'], mode='lines', name='Banda Superior', line=dict(color='green')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['lower_band'], mode='lines', name='Banda Inferior', line=dict(color='red')), row=1, col=1)

    if moving_averages:
        fig.add_trace(go.Scatter(x=df.index, y=df['fast_ma'], mode='lines', name='Media Móvil Rápida', line=dict(color='orange')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['slow_ma'], mode='lines', name='Media Móvil Lenta', line=dict(color='green')), row=1, col=1)

    if 'signal' in df.columns:
        buy_signals = df[df['signal'] == 1]
        fig.add_trace(go.Scatter(
            x=buy_signals.index, y=buy_signals['close'],
            mode='markers', name='Señal de Compra',
            marker=dict(color='green', size=10, symbol='triangle-up')
        ), row=1, col=1)

        sell_signals = df[df['signal'] == -1]
        fig.add_trace(go.Scatter(
            x=sell_signals.index, y=sell_signals['close'],
            mode='markers', name='Señal de Venta',
            marker=dict(color='red', size=10, symbol='triangle-down')
        ), row=1, col=1)

    if rsi is not None:
        fig.add_trace(go.Scatter(x=rsi.index, y=rsi['rsi'], mode='lines', name='RSI', line=dict(color='purple')), row=2, col=1)
        fig.add_hline(y=70, line=dict(color='red', dash='dash'), row=2, col=1)
        fig.add_hline(y=65, line=dict(color='orange', dash='dash'), row=2, col=1)
        fig.add_hline(y=40, line=dict(color='orange', dash='dash'), row=2, col=1)
        fig.add_hline(y=30, line=dict(color='green', dash='dash'), row=2, col=1)

    if volatility is not None:
        fig.add_trace(go.Scatter(x=volatility.index, y=volatility['volatility'], mode='lines', name='Volatilidad', line=dict(color='black')), row=rows, col=1)

    if trend is not None:
        fig.add_trace(go.Scatter(x=trend.index, y=trend['y_predict'], mode='lines', name='Regresión Lineal', line=dict(color='red', dash='dash')), row=1, col=1)

    fig.update_layout(
        title='Financial Metrics Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_white'
    )

    # If a save_path is provided, persist the figure as HTML and PNG
    if save_path is not None:
        try:
            p = Path(save_path)
            # If a file path with extension was provided, strip it
            if p.suffix:
                p = p.with_suffix('')
            p.parent.mkdir(parents=True, exist_ok=True)
            html_path = str(p) + '.html'
            png_path = str(p) + '.png'
            # Write interactive HTML
            fig.write_html(html_path, include_plotlyjs='cdn')
            # Write static image (requires kaleido)
            try:
                fig.write_image(png_path)
            except Exception as e:
                # If kaleido is not installed the image export will fail; report and continue
                print('Warning: could not write PNG image (kaleido may be missing):', e)
            print(f'Figure saved to: {html_path} and {png_path}')
        except Exception as e:
            print('Error saving figure:', e)

    # Show interactive figure in interactive environments only if requested
    if show:
        fig.show()
