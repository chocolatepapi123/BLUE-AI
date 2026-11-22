from pathlib import Path
import json, re
root=Path(__file__).resolve().parents[1]
required=['index.html','styles.css','app.js','manifest.json','service-worker.js','README.md','docs/PHONE_GUIDE.md','docs/ROADMAP_AND_LIMITS.md','docs/CSV_FORMAT.md','.github/workflows/blue-ai-upload.yml']
missing=[f for f in required if not (root/f).is_file()]
if missing: raise SystemExit(f'Missing package files: {missing}')
html=(root/'index.html').read_text()
js=(root/'app.js').read_text()
for selector in ['overview','knowledge','strategies','market','backtest','signals','discipline']:
    if f'id="{selector}"' not in html: raise SystemExit(f'Missing HTML section: {selector}')
for required_feature in ['parseCSV','sweepSignal','runBT','analyzeMaterial','Backup all data']:
    if required_feature not in html+js: raise SystemExit(f'Missing code marker: {required_feature}')
markets=['EURUSD','GBPUSD','XAUUSD','XAGUSD','NAS100','SPX500','US30']
for market in markets:
    if market not in html: raise SystemExit(f'Market missing from UI: {market}')
manifest=json.loads((root/'manifest.json').read_text())
if manifest.get('name')!='BLUE AI Trading Research': raise SystemExit('Manifest invalid')
print('BLUE AI static smoke check: PASS')
print('Validated sections, expected market symbols, manifest, docs and workflow.')
