# Roadmap and honest feature status

## Present in this package
- Responsive single-page app; navigation sections
- Local browser storage
- Knowledge notes/transcript entry and YouTube URL metadata
- Keyword tagging for a limited set of concepts
- PDF text extraction via PDF.js CDN import (requires internet)
- Strategy profile CRUD, market assignment, timeframe and session metadata
- OHLC CSV importer for seven instruments and six timeframe selections
- Sample range sweep backtester, trade list and basic R metrics
- Latest-bar signal scan using the sample rule
- Discipline checklist and personal settings
- JSON backup/restore
- Basic service worker cache
- ZIP installer workflow for GitHub Actions

## Not implemented (do not advertise as implemented)
- Semantic AI/LLM strategy understanding or video ingestion
- Automated YouTube transcript fetching
- Strategy rule execution from natural-language profiles
- Full ICT/SMC model library or chart drawing
- Live market feeds or continuous scanning
- Timezone/session logic or news/calendar feed
- Realistic spread, commission, slippage, partial fills or broker-specific CFDs
- Walk-forward, out-of-sample, Monte Carlo, parameter search, optimizer or adaptive learning
- Persistent cloud database/sync or cloud jobs
- Telegram alerts or browser push notifications
- Broker connections, order execution or account risk enforcement
- Cross-timeframe synchronized analysis

## Upgrade gates
Each major feature must be added with tests and documented limits before calling it complete. Strategy candidates must be tested out-of-sample and forward paper-traded before considering live use. This project should remain research-only unless separately audited.
