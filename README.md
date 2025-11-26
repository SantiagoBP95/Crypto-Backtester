# Trading Project

A small Python project for downloading historical price data from Binance, applying simple trading strategies (mean reversion and momentum), running lightweight backtests, and generating metrics and plots for analysis. This repository is intended for local experimentation and educational use, not for production trading.

Repository structure:

- `src/` : source code (data fetch, strategies, metrics, backtesting, classifier)
- `.env.example` : example environment variables file (copy to `.env` and fill in)
- `requirements.txt` : Python dependencies
- `results/` : saved backtest CSVs and plot HTML files

Quick start

1. Copy the example environment file and add your credentials locally (do NOT commit secrets):

```powershell
copy .env.example .env
```

2. Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Run the demo runner (downloads data, applies a strategy, runs a simple backtest, and saves results):

```powershell
python run.py --strategy mean_reverse --days 30
```

Notes

- The file `src/config.py` and `.env.example` contain placeholder values (`XXXXXX`); replace them locally or prefer setting environment variables instead.
- This project uses the `python-binance` client. Make sure your API key has the appropriate permissions and avoid publishing keys with push/pull access.
- The runner (`run.py`) is intended for local demos only. It is not hardened for production trading (no slippage, commissions, execution engine, or risk controls).

Publishing checklist

- Remove or mask any real API keys or secrets from all files.
- Add a `.gitignore` entry for `.env` and `.venv/` if not already present.
- Consider adding a `CONTRIBUTING.md` and `LICENSE` before publishing.
- Add more explicit documentation on intended use and the disclaimers for financial risk.