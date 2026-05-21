"""FRED (Federal Reserve Economic Data) API wrapper for the Sector Rotation course."""
from __future__ import annotations

import pandas as pd
import requests
import streamlit as st

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES_INFO: dict[str, dict] = {
    "T10Y2Y": {
        "name_he": "מרווח עקום התשואות 10Y-2Y",
        "name_en": "10-Year minus 2-Year Treasury Spread",
        "unit": "%",
        "interpretation": "ערך שלילי (היפוך) מבשר על מיתון; ערך גבוה ועולה מעיד על התרחבות.",
    },
    "DGS10": {
        "name_he": "תשואת אג\"ח ממשלתי 10 שנים",
        "name_en": "10-Year Treasury Constant Maturity Rate",
        "unit": "%",
        "interpretation": "תשואות גבוהות מאותתות ציפיות צמיחה/אינפלציה; נפילה חדה - חשש מהאטה.",
    },
    "DGS2": {
        "name_he": "תשואת אג\"ח ממשלתי שנתיים",
        "name_en": "2-Year Treasury Constant Maturity Rate",
        "unit": "%",
        "interpretation": "רגיש לציפיות ריבית הפד; עלייה מהירה - הקשחה מוניטרית צפויה.",
    },
    "FEDFUNDS": {
        "name_he": "ריבית הפד (Effective)",
        "name_en": "Effective Federal Funds Rate",
        "unit": "%",
        "interpretation": "ריבית עולה - שלב מאוחר במחזור; ריבית יורדת - תמיכה בצמיחה.",
    },
    "UNRATE": {
        "name_he": "שיעור אבטלה",
        "name_en": "Unemployment Rate",
        "unit": "%",
        "interpretation": "אבטלה נמוכה - שיא מחזור; עלייה מעל ממוצע נע 12 חודשים - סיגנל Sahm למיתון.",
    },
    "ICSA": {
        "name_he": "תביעות אבטלה ראשוניות",
        "name_en": "Initial Jobless Claims",
        "unit": "Thousands",
        "interpretation": "אינדיקטור מקדים; עלייה מתמשכת מעל 300K - חולשה בשוק העבודה.",
    },
    "CPIAUCSL": {
        "name_he": "מדד המחירים לצרכן (CPI)",
        "name_en": "Consumer Price Index, All Urban Consumers",
        "unit": "Index",
        "interpretation": "אינפלציה גבוהה מאלצת הקשחה; ירידה חדה - סיכון דפלציה.",
    },
    "PCEPI": {
        "name_he": "מדד מחירי PCE",
        "name_en": "Personal Consumption Expenditures Price Index",
        "unit": "Index",
        "interpretation": "מדד האינפלציה המועדף על הפד; היעד 2% YoY.",
    },
    "INDPRO": {
        "name_he": "ייצור תעשייתי",
        "name_en": "Industrial Production Index",
        "unit": "Index",
        "interpretation": "עלייה - התרחבות מחזורית; ירידה רצופה - האטה/מיתון.",
    },
    "UMCSENT": {
        "name_he": "סנטימנט הצרכן (מישיגן)",
        "name_en": "University of Michigan Consumer Sentiment",
        "unit": "Index",
        "interpretation": "ערכים נמוכים היסטורית מקדימים לעיתים תחתית בשוק.",
    },
    "PERMIT": {
        "name_he": "אישורי בנייה",
        "name_en": "New Private Housing Units Authorized by Building Permits",
        "unit": "Thousands",
        "interpretation": "אינדיקטור מקדים לפעילות נדל\"ן וצמיחה; ירידה מתמשכת - סיכון מיתון.",
    },
    "HOUST": {
        "name_he": "התחלות בנייה",
        "name_en": "Housing Starts",
        "unit": "Thousands",
        "interpretation": "רגיש מאוד לריבית; שיא בשלב מוקדם, שפל בתחתית מחזור.",
    },
    "RSAFS": {
        "name_he": "מכירות קמעונאיות",
        "name_en": "Advance Retail Sales: Retail and Food Services",
        "unit": "Millions USD",
        "interpretation": "אינדיקטור ביקוש הצרכן; חולשה ב-YoY ריאלי - חשש למיתון.",
    },
    "BAMLH0A0HYM2": {
        "name_he": "מרווח אג\"ח High Yield (OAS)",
        "name_en": "ICE BofA US High Yield Option-Adjusted Spread",
        "unit": "%",
        "interpretation": "מרווחים מתרחבים - סטרס פיננסי; מרווחים נמוכים - תיאבון סיכון גבוה.",
    },
    "M2SL": {
        "name_he": "היצע הכסף M2",
        "name_en": "M2 Money Stock",
        "unit": "Billions USD",
        "interpretation": "צמיחת M2 גבוהה - תמיכה במחזור; ירידה ב-YoY - הידוק נדיר היסטורית.",
    },
    "PAYEMS": {
        "name_he": "משרות לא חקלאיות (NFP)",
        "name_en": "All Employees, Total Nonfarm",
        "unit": "Thousands",
        "interpretation": "עלייה רצופה - התרחבות; ירידה ב-YoY - מיתון כמעט תמיד.",
    },
}


def _get_api_key() -> str:
    try:
        key = st.secrets["fred_api_key"]
    except (KeyError, FileNotFoundError):
        raise RuntimeError(
            "מפתח FRED API חסר. הגדר את st.secrets[\"fred_api_key\"] בקובץ "
            ".streamlit/secrets.toml (מקומי) או בהגדרות Secrets של Streamlit Cloud. "
            "ניתן להשיג מפתח חינמי בכתובת https://fred.stlouisfed.org/docs/api/api_key.html"
        )
    if not key:
        raise RuntimeError("מפתח FRED API ריק. ודא ש-st.secrets[\"fred_api_key\"] מכיל מחרוזת תקפה.")
    return str(key)


@st.cache_data(ttl=21600, show_spinner=False)
def get_series(series_id: str, start: str = "2000-01-01") -> pd.DataFrame:
    """Fetch a single FRED series; returns DataFrame indexed by date with column 'value'."""
    try:
        api_key = _get_api_key()
    except RuntimeError:
        raise
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start,
    }
    try:
        resp = requests.get(FRED_URL, params=params, timeout=15)
        resp.raise_for_status()
        observations = resp.json().get("observations", [])
    except (requests.RequestException, ValueError) as exc:
        st.warning(f"שגיאת רשת בשליפת {series_id} מ-FRED: {exc}")
        return pd.DataFrame(columns=["value"]).astype({"value": float})

    if not observations:
        return pd.DataFrame(columns=["value"]).astype({"value": float})

    df = pd.DataFrame(observations)
    df = df[df["value"] != "."].copy()
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"]).set_index("date")[["value"]].sort_index()
    return df


@st.cache_data(ttl=21600, show_spinner=False)
def get_many(series_ids: list[str], start: str = "2000-01-01") -> dict[str, pd.DataFrame]:
    """Fetch multiple FRED series; returns dict mapping series_id -> DataFrame."""
    return {sid: get_series(sid, start=start) for sid in series_ids}


def latest_value(df: pd.DataFrame) -> tuple[pd.Timestamp, float]:
    """Return (date, value) of the most recent observation; (NaT, NaN) if df is empty."""
    if df is None or df.empty or "value" not in df.columns:
        return pd.NaT, float("nan")
    last = df["value"].dropna()
    if last.empty:
        return pd.NaT, float("nan")
    return last.index[-1], float(last.iloc[-1])


def pct_change_yoy(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'yoy_pct' column with 12-month percent change."""
    out = df.copy()
    if out.empty or "value" not in out.columns:
        out["yoy_pct"] = pd.Series(dtype=float)
        return out
    out["yoy_pct"] = out["value"].pct_change(periods=12) * 100.0
    return out


def zscore_recent(df: pd.DataFrame, lookback_years: int = 5) -> float:
    """Z-score of the latest value vs the trailing `lookback_years` window."""
    if df is None or df.empty or "value" not in df.columns:
        return float("nan")
    s = df["value"].dropna()
    if s.empty:
        return float("nan")
    cutoff = s.index[-1] - pd.DateOffset(years=lookback_years)
    window = s.loc[s.index >= cutoff]
    if len(window) < 2:
        return float("nan")
    std = window.std()
    if std == 0 or pd.isna(std):
        return float("nan")
    return float((s.iloc[-1] - window.mean()) / std)
