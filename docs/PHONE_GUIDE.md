# BLUE AI Phone Guide (Android)

## Open the app
1. Download and unzip BLUE AI using your phone's file manager.
2. Open the extracted folder and tap `index.html`.
3. If Android asks which app, use a modern browser (Chrome recommended). If file:// blocks functions, use free static hosting (GitHub Pages) by uploading the app files to a repository root.
4. App is designed for a phone screen.

## Add learning material
- YouTube: paste the URL and transcript into the text box; video transcripts cannot be fetched automatically by this browser build.
- PDF: tap Choose PDF, select a PDF, wait for extraction, then tap Analyze & save. PDF parser loads from a free public CDN, so first-time PDF extraction requires internet.
- Notes: choose Notes / pasted text, paste content and Analyze & save.
- Concept tags are basic keyword detection. Always review and correct the notes yourself.

## Import candles
Choose market and timeframe. Select CSV with open, high, low, close columns (case-insensitive); timestamp is optional and volume is ignored. Ensure chronological order. Start with smaller files because browser storage has a quota.

## Backtest
Select market/timeframe that has data. Adjust range lookback and RR, then Run backtest. This is only a simple illustrative range-sweep model. No session filter, spread, commission, slippage or live prices. Use CSV timestamps and candles from a reliable source, and don't treat results as investment evidence.

## Backups
Tap Backup all data; save the downloaded JSON somewhere safe. To restore, tap Restore backup and select the JSON. Reset app permanently clears local browser data.
