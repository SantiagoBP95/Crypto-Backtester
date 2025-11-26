"""Example main runner.

This script is a convenience entrypoint for demos: it downloads recent
price data, applies the selected strategy, runs the simplified backtest,
stores the results and optionally displays charts. It is intended for
local demonstration and README examples (not for production execution).
"""

import os
import sys
import argparse
from pathlib import Path

# Ensure that `src` is importable, allowing relative imports for the demo
ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'src'
sys.path.insert(0, str(SRC))

# Import the modules from the `src` package
import get_binance_data as gbd
import backtest as bt
import metrics as m
import mean_reverse as mr
import momentum as mom


def ensure_results_dir():
    """Create and return the results directory path."""
    results = ROOT / 'results'
    results.mkdir(exist_ok=True)
    return results


def parse_args():
    """Parse command line arguments for the demo runner."""
    p = argparse.ArgumentParser(description='Demo runner for trading project')
    p.add_argument('--strategy', choices=['mean_reverse', 'momentum'], default='mean_reverse')
    p.add_argument('--days', type=int, default=30)
    p.add_argument('--symbol', type=str, default='BTCUSDT')
    p.add_argument('plot', action='store_true', help='Display interactive plots')
    return p.parse_args()


def main():
    args = parse_args()
    results_dir = ensure_results_dir()

    print(f"Downloading {args.days} days of data for {args.symbol}...")
    df = gbd.get_binance_data(symbol=args.symbol, days=args.days)

    print(f"Applying strategy: {args.strategy}")
    if args.strategy == 'mean_reverse':
        signal, df_strategy = mr.apply_mean_reverse(df, 20)
        # Merge the close price with the indicators for plotting
        df_plot = df[['close']].join(df_strategy, how='right')
    else:
        signal, df_strategy = mom.apply_momentum(df, 20)
        df_plot = df_strategy

    print('Running simulated backtest...')
    backtest_df = bt.ejecutar_backtest(df_plot)
    backtest_df = bt.calcular_precio_promedio(backtest_df)
    backtest_df = bt.construir_curva_rentabilidad(backtest_df)

    # Save results to CSV for inspection
    out_csv = results_dir / f'backtest_{args.strategy}.csv'
    backtest_df.to_csv(out_csv)
    print(f'Results saved to: {out_csv}')

    # Compute a couple of basic metrics and print them
    try:
        sharpe = m.calculate_sharpe_ratio(df_plot)
        mdd = m.calculate_max_drawdown(df_plot)
        print(f'Sharpe (approx): {sharpe:.4f}, Max Drawdown: {mdd:.4f}')
    except Exception as e:
        print('Could not compute metrics:', e)

    # Always call the plotting helper so plots are saved; control display with `show`
    try:
        save_base = results_dir / f'plot_{args.strategy}'
        show_plot = args.plot
        if args.strategy == 'mean_reverse':
            m.plot(df_plot, bollinger_bands=True, save_path=save_base, show=show_plot)
        else:
            m.plot(df_plot, moving_averages=True, rsi=df_plot[['rsi']], save_path=save_base, show=show_plot)
    except Exception as e:
        print('Error showing or saving plot:', e)

    print('Run completed.')


if __name__ == '__main__':
    main()
