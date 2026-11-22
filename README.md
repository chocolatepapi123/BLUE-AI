# BLUE AI — Offline-first Trading Research App

BLUE AI is a mobile-friendly, local-first browser application for trading notes, rule-based strategy profiles, importing OHLC candle CSV files, backtesting a sample liquidity-sweep rule, and generating signals from imported bars.

## Straight status / scope

This is a **working research prototype**, not a finished autonomous AI trader. It has no LLM: trading concepts are tagged by keyword rules. The demo strategy is a 20-bar range sweep/close-back-inside pattern with configurable lookback and reward:risk. It is not ICT/SMC implementation breadth, and its performance is not evidence of an edge. YouTube URLs are saved, but transcript text must be pasted manually. PDF extraction uses PDF.js from a public CDN and therefore needs internet when loading the PDF parser. No paid API keys are used.

No live quote feed, automatic multi-market continuous scanner, broker integration, trade execution, real-time Telegram delivery, session-time filtering, spread/slippage model, or advanced learning/optimization is included in this version. Signal scan is over the most recent imported candle per market/timeframe. Data, settings and knowledge are stored in the browser localStorage and can be lost if browser data is cleared; use backups. Local browser storage is limited, so import modest candle CSVs. No guarantee of continuous background monitoring while the browser is closed.

## Run on Android
1. Extract the ZIP on a computer or phone file manager.
2. Open `index.html` in a modern browser. Some browsers restrict offline/PWA features on `file://`; for full PWA install behavior, host static files on GitHub Pages or Vercel (free tiers may change).
3. App features work locally after page opens; PDF extraction needs internet for the PDF.js CDN module.
4. Use Backup all data regularly to export JSON and Restore backup to bring it back.

## Usage
- **Knowledge**: Add a note/transcript; save YouTube URL and pasted transcript together. Concept tags are keyword-based, not AI understanding. For PDF, tap Choose PDF, wait for text extraction, then Analyze & save.
- **Strategies**: Create per-market profiles. Rules are stored as text and concept tags; they are not automatically executable.
- **Market data**: Import OHLC CSV. Headers may include timestamp/time/date, open/high/low/close; volume optional. CSV bars are stored under selected market/timeframe.
- **Backtest**: Run the included 20-bar sweep example. Entering a sweep is modeled at signal candle close; stop is checked before target on each later candle (conservative same-candle handling). It does not model spread, commission, slippage, partials, gaps, or session windows. Historical performance is not predictive.
- **Signals**: Scan latest imported candles for the same sample rule. Signals are local journal records, not live feed alerts.
- **Discipline**: Local checklist plus personal max trades/day and daily loss-limit settings. This app does not enforce these on a broker or account.

## CSV example
```csv
timestamp,open,high,low,close,volume
2025-01-01T00:00:00Z,1.03,1.04,1.02,1.035,100
2025-01-01T01:00:00Z,1.035,1.05,1.03,1.045,150
```
Values must be numeric for OHLC. Candles are assumed chronologically; sort ascending before import.

## Files
- `index.html`, `styles.css`, `app.js`: frontend.
- `manifest.json`, `service-worker.js`: basic PWA/offline cache.
- `.github/workflows/blue-ai-upload.yml`: ZIP installer workflow; uploads into `incoming/` and triggers extraction/commit. Review it before enabling write permissions.
- `docs/`: mobile guide, data format and roadmap.

## Free-only stance
No paid APIs or keys are required for this local prototype. A genuinely robust live data feed, reliable cloud runtime, LLM video understanding, and always-on alerts may require resources; this version deliberately does not claim to provide them. Use only money-free services if expanding, and recheck their terms/quotas.

## Safety
Research/education only. Not financial advice. Do not use outputs to trade real money. Verify data and test independently. Backtesting can contain bias and cannot establish future profitability.
