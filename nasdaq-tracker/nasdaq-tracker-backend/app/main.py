from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import sqlite3
import os
import yfinance as yf
from datetime import datetime
import threading

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Database setup
DB_PATH = os.environ.get("DB_PATH", "/data/app.db")
if not os.path.exists(os.path.dirname(DB_PATH) or "."):
    DB_PATH = "app.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            stock_symbol TEXT NOT NULL,
            quantity REAL NOT NULL,
            purchase_price REAL NOT NULL,
            purchase_date TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


init_db()

# Cache for top gainers
top_gainers_cache: dict = {
    "data": [],
    "last_updated": None,
}
cache_lock = threading.Lock()

# Major NASDAQ-100 symbols for scanning
NASDAQ_SYMBOLS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "COST", "NFLX",
    "TMUS", "AMD", "ADBE", "PEP", "CSCO", "INTC", "INTU", "CMCSA", "TXN", "QCOM",
    "AMGN", "HON", "AMAT", "BKNG", "ISRG", "SBUX", "VRTX", "MDLZ", "GILD", "ADI",
    "LRCX", "REGN", "PANW", "MU", "KLAC", "SNPS", "CDNS", "MELI", "PYPL", "CRWD",
    "CTAS", "MAR", "ORLY", "ABNB", "MRVL", "FTNT", "DASH", "CEG", "WDAY", "CSX",
    "ADSK", "CHTR", "PCAR", "MNST", "ROP", "FANG", "AEP", "PAYX", "ODFL", "FAST",
    "KDP", "CPRT", "AZN", "ROST", "DXCM", "EA", "VRSK", "KHC", "CTSH", "MCHP",
    "LULU", "GEHC", "EXC", "IDXX", "CCEP", "BKR", "TTD", "ON", "BIIB", "CSGP",
    "CDW", "ZS", "ANSS", "TTWO", "GFS", "DDOG", "ILMN", "WBD", "MDB", "TEAM",
    "ARM", "SMCI", "COIN", "MSTR", "PLTR", "ROKU", "ZM", "OKTA", "SNOW", "NET",
]


class InvestmentCreate(BaseModel):
    customer_name: str
    stock_symbol: str
    quantity: float
    purchase_price: float
    purchase_date: str



def fetch_top_gainers() -> list[dict]:
    """Fetch top 10 NASDAQ gainers by daily percentage change."""
    try:
        gainers: list[dict] = []
        symbols_str = " ".join(NASDAQ_SYMBOLS)
        tickers = yf.Tickers(symbols_str)

        for symbol in NASDAQ_SYMBOLS:
            try:
                ticker = tickers.tickers.get(symbol)
                if ticker is None:
                    continue
                info = ticker.fast_info
                current_price = info.last_price
                prev_close = info.previous_close
                if current_price and prev_close and prev_close > 0:
                    change = current_price - prev_close
                    pct_change = (change / prev_close) * 100
                    gainers.append({
                        "symbol": symbol,
                        "name": symbol,
                        "price": round(current_price, 2),
                        "change": round(change, 2),
                        "pct_change": round(pct_change, 2),
                    })
            except Exception:
                continue

        gainers.sort(key=lambda x: x["pct_change"], reverse=True)
        return gainers[:10]
    except Exception as e:
        print(f"Error fetching gainers: {e}")
        return []


def get_stock_names(symbols: list[str]) -> dict[str, str]:
    """Get company names for symbols."""
    names: dict[str, str] = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            names[symbol] = info.get("shortName", symbol)
        except Exception:
            names[symbol] = symbol
    return names


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/api/top-gainers")
def get_top_gainers():
    """Get top 10 NASDAQ stocks by daily gains."""
    with cache_lock:
        now = datetime.now()
        if (
            top_gainers_cache["last_updated"]
            and (now - top_gainers_cache["last_updated"]).total_seconds() < 300
            and top_gainers_cache["data"]
        ):
            return {
                "gainers": top_gainers_cache["data"],
                "last_updated": top_gainers_cache["last_updated"].isoformat(),
            }

    gainers = fetch_top_gainers()

    if gainers:
        symbols = [g["symbol"] for g in gainers]
        names = get_stock_names(symbols)
        for g in gainers:
            g["name"] = names.get(g["symbol"], g["symbol"])

    with cache_lock:
        if gainers:
            top_gainers_cache["data"] = gainers
            top_gainers_cache["last_updated"] = datetime.now()
        cached_gainers = top_gainers_cache["data"]
        updated_at = top_gainers_cache["last_updated"]

    return {
        "gainers": gainers if gainers else cached_gainers,
        "last_updated": updated_at.isoformat() if updated_at else None,
    }


@app.get("/api/investments")
def get_investments():
    """Get all customer investments."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM investments ORDER BY created_at DESC").fetchall()
    conn.close()
    investments = [dict(row) for row in rows]
    return {"investments": investments}


@app.post("/api/investments")
def create_investment(investment: InvestmentCreate):
    """Add a new customer investment."""
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO investments (customer_name, stock_symbol, quantity, purchase_price, purchase_date) VALUES (?, ?, ?, ?, ?)",
        (
            investment.customer_name,
            investment.stock_symbol.upper(),
            investment.quantity,
            investment.purchase_price,
            investment.purchase_date,
        ),
    )
    conn.commit()
    investment_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM investments WHERE id = ?", (investment_id,)).fetchone()
    conn.close()
    return {"investment": dict(row)}


@app.delete("/api/investments/{investment_id}")
def delete_investment(investment_id: int):
    """Delete a customer investment."""
    conn = get_db()
    row = conn.execute("SELECT * FROM investments WHERE id = ?", (investment_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Investment not found")
    conn.execute("DELETE FROM investments WHERE id = ?", (investment_id,))
    conn.commit()
    conn.close()
    return {"message": "Investment deleted"}


@app.get("/api/investments/portfolio")
def get_portfolio_summary():
    """Get portfolio summary with current stock prices."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM investments ORDER BY customer_name, stock_symbol").fetchall()
    conn.close()

    if not rows:
        return {"portfolio": [], "total_invested": 0, "total_current_value": 0, "total_gain_loss": 0, "total_gain_loss_pct": 0}

    investments = [dict(row) for row in rows]
    symbols = list(set(inv["stock_symbol"] for inv in investments))

    current_prices: dict[str, float] = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.fast_info.last_price
            if price:
                current_prices[symbol] = round(price, 2)
        except Exception:
            pass

    total_invested = 0.0
    total_current = 0.0
    portfolio = []

    for inv in investments:
        invested = inv["quantity"] * inv["purchase_price"]
        current_price = current_prices.get(inv["stock_symbol"], inv["purchase_price"])
        current_value = inv["quantity"] * current_price
        gain_loss = current_value - invested
        gain_loss_pct = (gain_loss / invested * 100) if invested > 0 else 0

        total_invested += invested
        total_current += current_value

        portfolio.append({
            **inv,
            "current_price": current_price,
            "invested_value": round(invested, 2),
            "current_value": round(current_value, 2),
            "gain_loss": round(gain_loss, 2),
            "gain_loss_pct": round(gain_loss_pct, 2),
        })

    return {
        "portfolio": portfolio,
        "total_invested": round(total_invested, 2),
        "total_current_value": round(total_current, 2),
        "total_gain_loss": round(total_current - total_invested, 2),
        "total_gain_loss_pct": round(((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0, 2),
    }


@app.get("/api/stock/price/{symbol}")
def get_stock_price(symbol: str):
    """Get current price for a stock symbol."""
    try:
        ticker = yf.Ticker(symbol.upper())
        price = ticker.fast_info.last_price
        if price:
            return {"symbol": symbol.upper(), "price": round(price, 2)}
        raise HTTPException(status_code=404, detail="Price not available")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Stock not found: {str(e)}")
