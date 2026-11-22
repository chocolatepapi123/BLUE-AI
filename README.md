# BLUE AI — Trading Research & Strategy Validation

BLUE AI is a mobile-friendly local web application with a deterministic trading-research engine. It does **not** place orders. It is intended for research, replay, and validation—not financial advice.


## Implemented features

- Persistent local JSON storage for knowledge items, strategy profiles, datasets, settings, and signal history.
- CSV OHLCV import (time/date + open/high/low/close; volume optional), validation, candle storage.
- Free-data fetch adapter for Yahoo Finance chart data (unofficial, rate-limited; proxy tickers are not broker/CFD prices). Supports M5, M15, M30, H1, H4 aggregation, D1 where provider permits.
- Deterministic candle analysis: range bias, swing pivots, recent sweep flags, displacement, 3-candle FVG, and structured sweep+displacement signal conditions.
- Rule-model backtesting with configurable lookback, target R, risk, displacement multiplier, maximum price-risk filter, spread and slippage assumptions, max holding period, conservative stop-first handling when SL/TP hit in the same candle, and summary metrics/trade list.
- Parameter grid research with chronological 70/30 train/holdout split, 27 combinations, and holdout metrics. This is a simple holdout test, not full walk-forward or Monte Carlo.
- Multi-dataset timeframe bias comparison (simple midpoint bias, not predictive).
- Knowledge library: notes, pasted transcripts, PDF text extraction in browser, URL references, concept tagging, optional YouTube transcript fetch when captions are accessible and optional dependency installed.
- Strategy profile CRUD. Profiles are currently saved/organized but **are not dynamically compiled into backtest rules**; backtest uses the built-in sweep/displacement rule.
- Research report based on deterministic concept tags and backtest metrics.
- Optional local Ollama chat integration (requires Ollama installed and a local model pulled). No hosted AI API key is needed.
- Optional Telegram alert delivery (user-provided bot token/chat ID), scheduled scanning of stored candles, optional scheduled free-market data refresh while backend remains running.
- JSON export/restore and destructive reset.
- PWA shell caching; API and stored data remain local to the backend runtime.

## Run on Android using Termux

1. Install **Termux from F-Droid** (avoid the outdated Play Store version).
2. Open Termux and run:
   ```sh
   pkg update -y && pkg install python unzip -y
   ```
3. Extract this ZIP in Termux or your shared Downloads directory. If using shared storage first run `termux-setup-storage`.
4. Change to the extracted `blue-ai` folder and run:
   ```sh
   python -m pip install -r requirements.txt
   python server.py
   ```
5. Keep Termux running; open Chrome and visit **http://127.0.0.1:8765**.
6. For reliable scheduled scans, disable Android battery optimization for Termux. The server must remain running; Android can still stop background processes.

On desktop, use Python 3.10+ and run the same commands. `run-blue-ai.bat` is a Windows launcher.

## Market-data fetching

The Fetch interface uses Yahoo Finance's unofficial chart endpoint. Symbol mappings include EURUSD/GBPUSD/USDJPY, gold/silver futures proxies, and US index futures proxies. Data can be delayed, incomplete, unavailable for an interval, or unlike a broker's CFD. If fetch fails, import broker/platform OHLC CSV.

For H4, hourly candles are aggregated into groups of four. Time boundaries may not match a broker's native H4 session candles.

## AI options

- Technical analysis, scanner, backtest, concept tagging and report work without an LLM.
- Optional YouTube captions are fetched using `youtube-transcript-api`; availability depends on captions, access, and library/API changes.
- Optional local AI assistant uses **Ollama** at `http://127.0.0.1:11434`. Install Ollama, pull a model (e.g. `ollama pull llama3.2`), and run Ollama on the same machine as the backend. On Android, Ollama generally is not practical for many phones; the core deterministic engine remains available.
- BLUE does not autonomously train a model from content, understand video frames/audio, rewrite itself, or verify strategy claims. It stores transcripts and indexes concepts. Strategy profiles are notes/structured metadata, not automatically executable rules yet.

## Telegram

Create a bot via Telegram BotFather, start a chat with it, obtain the chat ID, and add token/chat ID in Settings. Secrets are stored in the local settings JSON—keep this device and backup secure. Alerts are generated only when a scanner condition is found.


## GitHub Pages / web hosting caveat

GitHub Pages only serves static files; it cannot run this Python API, persist backend JSON files, run Ollama, or execute the scheduler. To use the full app, run the Python backend locally (Termux/PC) or deploy it to a Python-capable persistent backend host. Free hosts can sleep and have ephemeral storage; the local JSON store is not designed for serverless deployment. The ZIP uploader workflow is included under `.github/workflows/blue-ai-upload.yml`; GitHub's protections mean workflow files must be installed/committed separately rather than extracted by that ZIP workflow.

## Tests

```sh
python -m unittest discover -s tests -v
python -m py_compile server.py engine/core.py
node --check web/app.js
```

## Safety / limitations

- Research only; no broker connection, execution, trade copying, or guarantee of profitability.
- Sweep detection and midpoint bias are simple rule definitions; ICT/SMC concepts vary by practitioner and are not universally objective.
- Backtests are affected by candle quality, costs, slippage, intra-bar ambiguity and selection bias. When SL and TP occur in the same candle, the engine counts SL first. Optimization can overfit; the 70/30 holdout is a modest check, not proof.
- Automatic scanner uses stored data. Refresh option requests data from a free provider each scheduled run and may fail/rate-limit. Scheduler works only while backend process remains alive.
- Strategy profiles are not yet interpreted as executable rule graphs. No automatic strategy learning, semantic model ingestion, image/video understanding, or autonomous self-improvement.
- Protect Telegram tokens and downloaded market files. Backup/restore is provided for local JSON state.


## Autonomous research batch (experimental)

Knowledge page now supports batch YouTube links and multiple PDF/text uploads. Captions are fetched when available; PDF text is extracted in the browser; keyword/regex extraction detects a limited list of instruments, timeframes, sessions and setup concepts; it then attempts free Yahoo Finance proxy-data retrieval and runs the built-in sweep/displacement backtest across detected markets/timeframes (or exploratory defaults). Batch reports are stored locally. This is an experimental workflow: it does **not** infer complete strategy rules semantically, compile extracted rules into executable strategies, or validate the extracted strategy itself. Backtest results are only for the existing baseline rule.
