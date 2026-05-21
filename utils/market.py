"""Market data utilities wrapping yfinance for SPDR sector ETFs."""
from __future__ import annotations

import pandas as pd
import streamlit as st
import yfinance as yf

SECTORS: dict[str, dict[str, str]] = {
    "XLB": {"name_he": "חומרי גלם", "name_en": "Materials", "emoji": "🧱"},
    "XLC": {"name_he": "תקשורת", "name_en": "Communication", "emoji": "📡"},
    "XLE": {"name_he": "אנרגיה", "name_en": "Energy", "emoji": "⛽"},
    "XLF": {"name_he": "פיננסים", "name_en": "Financials", "emoji": "🏦"},
    "XLI": {"name_he": "תעשייה", "name_en": "Industrials", "emoji": "🏭"},
    "XLK": {"name_he": "טכנולוגיה", "name_en": "Technology", "emoji": "💻"},
    "XLP": {"name_he": "מוצרי צריכה בסיסיים", "name_en": "Consumer Staples", "emoji": "🛒"},
    "XLRE": {"name_he": "נדל\"ן", "name_en": "Real Estate", "emoji": "🏢"},
    "XLU": {"name_he": "שירותים ציבוריים", "name_en": "Utilities", "emoji": "💡"},
    "XLV": {"name_he": "בריאות", "name_en": "Healthcare", "emoji": "🩺"},
    "XLY": {"name_he": "צריכה לא-הכרחית", "name_en": "Consumer Discretionary", "emoji": "🛍️"},
}

BENCHMARK = "SPY"
SECTOR_TICKERS: list[str] = list(SECTORS.keys())


@st.cache_data(ttl=3600)
def get_prices(
    tickers: list[str], period: str = "5y", interval: str = "1wk"
) -> pd.DataFrame:
    """Fetch adjusted close prices as a wide DataFrame indexed by Date."""
    if not tickers:
        return pd.DataFrame()
    try:
        data = yf.download(
            tickers=tickers,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True,
            group_by="column",
            threads=True,
        )
        if data is None or data.empty:
            st.warning("לא התקבלו נתונים מ-yfinance.")
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):
            if "Close" in data.columns.get_level_values(0):
                close = data["Close"]
            else:
                close = data.xs("Close", axis=1, level=-1)
        else:
            col = "Close" if "Close" in data.columns else data.columns[0]
            close = data[[col]].rename(columns={col: tickers[0]})

        if isinstance(close, pd.Series):
            close = close.to_frame(name=tickers[0])

        close = close.dropna(how="all")
        close.index = pd.to_datetime(close.index)
        existing = [t for t in tickers if t in close.columns]
        return close[existing] if existing else close
    except Exception as exc:  # noqa: BLE001
        st.warning(f"שגיאה בשליפת נתוני שוק: {exc}")
        return pd.DataFrame()


def get_sector_prices(period: str = "5y", interval: str = "1wk") -> pd.DataFrame:
    """Fetch prices for all 11 SPDR sector ETFs plus the SPY benchmark."""
    return get_prices(SECTOR_TICKERS + [BENCHMARK], period=period, interval=interval)


def relative_strength(
    prices: pd.DataFrame, benchmark: str = "SPY"
) -> pd.DataFrame:
    """Compute relative strength vs benchmark, normalized to 100 at first valid row."""
    if prices.empty or benchmark not in prices.columns:
        return pd.DataFrame()
    bench = prices[benchmark]
    others = [c for c in prices.columns if c != benchmark]
    rs = prices[others].div(bench, axis=0)
    first_valid = rs.apply(lambda s: s.first_valid_index())
    base = pd.Series(
        {c: rs[c].loc[first_valid[c]] if first_valid[c] is not None else None for c in rs.columns}
    )
    rs = rs.div(base) * 100
    return rs


def momentum(prices: pd.DataFrame, lookback_weeks: int = 13) -> pd.Series:
    """Percentage return over the last N weeks per ticker."""
    if prices.empty:
        return pd.Series(dtype=float)
    if len(prices) <= lookback_weeks:
        return pd.Series(dtype=float, index=prices.columns)
    latest = prices.iloc[-1]
    past = prices.iloc[-1 - lookback_weeks]
    return ((latest / past) - 1.0) * 100


def rolling_returns(prices: pd.DataFrame, weeks: int) -> pd.DataFrame:
    """Rolling N-week percentage returns for each column."""
    if prices.empty or weeks <= 0:
        return pd.DataFrame(index=prices.index, columns=prices.columns)
    return (prices / prices.shift(weeks) - 1.0) * 100


def top_n(scores: pd.Series, n: int = 3) -> list[str]:
    """Return list of top N tickers by score, descending."""
    if scores is None or scores.empty:
        return []
    return scores.dropna().sort_values(ascending=False).head(n).index.tolist()
