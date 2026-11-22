# BLUE AI Trading Research (mobile-friendly, free local build)

This is a functional local research application, not an autonomous profitable trading AI. It runs using Python's standard library only; no API key or paid service is required.

## Run on Android (Termux)
1. Install Termux from F-Droid.
2. Open Termux and run `pkg update -y && pkg install python -y`.
3. Extract this ZIP into a folder in Termux (e.g. `~/blue-ai`).
4. `cd ~/blue-ai && python server.py`
5. Open Chrome and go to `http://127.0.0.1:8765`.

## Run on computer
Install Python 3.10+. In this folder run `python server.py`; open `http://localhost:8765`.

## Included functionality
- Knowledge store for pasted transcripts, notes, PDFs excerpts, articles and YouTube references. YouTube captions are **not fetched**; paste transcript content.
- Manual strategy profile CRUD/storage.
- CSV import and validation for OHLC candle data.
- Swing pivots, basic sweep/rejection, displacement and 3-candle FVG observation.
- Rule-based BUY/SELL scan from latest candle.
- Historical sweep/rejection backtest with R-metrics, stop-first same-bar rule and equity compounding.
- Deterministic keyword-based research report and backup export.
- Data persists to JSON files in `data/`.

## CSV format
Header names can be `timestamp`/`time`/`date`, `open`, `high`, `low`, `close`, optional `volume`. At least 10 valid rows required. Example:

```csv
timestamp,open,high,low,close,volume
2026-01-01 00:00,1.1000,1.1020,1.0990,1.1010,120
```

## Important boundaries
- This build is not an LLM, and does not semantically learn from videos or documents. Knowledge is stored; research summary uses keyword matching.
- Strategy profiles are saved as documentation; the backtester executes a built-in sweep + rejection + displacement model, not each profile's custom rules.
- No live quotes, broker API, order execution, auto-fetch YouTube transcript, Telegram bot, continuous hosted scanning, cloud sync, multi-timeframe confluence, spread/slippage/commission simulation, or walk-forward optimizer.
- Backtest is simplistic and can be biased. Candle OHLC cannot reveal intrabar path; stops are assumed hit first when stop and target both touched. It is for software testing/research only, not trading decisions.

## Tests
Run `python -m unittest discover -s tests -v`.
