# Testing NASDAQ Investment Tracker

## Environment Setup

### Backend
- Directory: `nasdaq-tracker/nasdaq-tracker-backend`
- Start: `poetry run fastapi dev app/main.py --port 8000`
- The backend auto-reloads on file changes via WatchFiles
- Health check: `curl http://localhost:8000/healthz`

### Frontend
- Directory: `nasdaq-tracker/nasdaq-tracker-frontend`
- Start: `npm run dev` (serves on http://localhost:5173)
- API URL configured in `.env` as `VITE_API_URL`

## Important Notes

### yfinance Loading Times
- The `/api/top-gainers` endpoint fetches ~100 NASDAQ symbols via yfinance on first call
- **First load takes 30-60 seconds** - be patient and don't assume it's broken
- Results are cached for 5 minutes, so subsequent calls are fast
- After a backend restart or code reload, the cache is cleared and the next call will be slow again
- The ANSS symbol may show "possibly delisted" warnings in backend logs - this is expected and harmless

### Database
- Local development uses `app.db` (SQLite) in the backend directory
- Deployed version uses `/data/app.db` on a persistent volume
- To reset test data, delete investments via the UI or the API: `curl -X DELETE http://localhost:8000/api/investments/{id}`

## Key Testing Flows

### 1. Top 10 Gainers Tab (default tab)
- Open http://localhost:5173
- Wait for data to load (spinner shows "Loading top gainers from NASDAQ...")
- Should display 10 rows with Symbol, Company, Price, Change, % Change
- All entries should have positive % Change values (sorted descending)
- Click "Refresh" to re-fetch (served from cache if < 5 min old)

### 2. Empty Portfolio Edge Case
- Delete all investments from the Investments tab
- Switch to Portfolio tab
- Should render without crash: shows $0.00 values and "No investments in portfolio" message
- This tests the `total_gain_loss_pct` field in the empty portfolio API response

### 3. Add Investment with Get Price
- Go to Investments tab
- Fill in Customer Name, Stock Symbol (e.g. NVDA)
- Click "Get Price" to auto-fill current market price
- Fill in Quantity and Purchase Date
- Click "Add Investment"
- Verify it appears in the Customer Investments table below

### 4. Portfolio with Live Data
- Switch to Portfolio tab after adding investments
- Verify summary cards: Total Invested, Current Value, Total Gain/Loss, Return %
- Verify portfolio table shows each investment with live current price and gain/loss calculations

## Devin Secrets Needed
No secrets are required for local testing. The app uses public Yahoo Finance data via the yfinance library.
