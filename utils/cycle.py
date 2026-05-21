"""Heuristic business cycle phase detector from FRED indicators.

Used by the Hebrew Sector Rotation Streamlit course to map current
macro indicator readings to one of four classic business cycle phases
(early / mid / late / recession) and to suggest sector tilts.
"""

from __future__ import annotations

PHASES = ["early", "mid", "late", "recession"]

PHASE_LABELS_HE: dict[str, str] = {
    "early": "🌱 התאוששות מוקדמת",
    "mid": "🚀 אמצע מחזור",
    "late": "🔥 סוף מחזור",
    "recession": "🧊 מיתון",
    "uncertain": "❓ לא ודאי",
}


def _get(indicators: dict, key: str):
    """Safe getter - returns None if key missing or value is not finite."""
    if not isinstance(indicators, dict):
        return None
    val = indicators.get(key)
    if val is None:
        return None
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    # Reject NaN
    if f != f:
        return None
    return f


def score_phase(indicators: dict) -> dict:
    """Score each phase in [0, 1] based on matching indicator conditions."""
    scores = {p: 0.0 for p in PHASES}

    t10y2y = _get(indicators, "T10Y2Y")
    unrate = _get(indicators, "UNRATE")
    unrate_chg = _get(indicators, "UNRATE_3m_chg")
    icsa_yoy = _get(indicators, "ICSA_yoy")
    cpi_yoy = _get(indicators, "CPIAUCSL_yoy")
    indpro_yoy = _get(indicators, "INDPRO_yoy")
    hy = _get(indicators, "BAMLH0A0HYM2")
    ff_chg = _get(indicators, "FEDFUNDS_6m_chg")
    umcsent_yoy = _get(indicators, "UMCSENT_yoy")

    # --- Recession ---
    if t10y2y is not None and t10y2y < 0:
        scores["recession"] += 0.20
    if unrate_chg is not None and unrate_chg > 0.2:
        scores["recession"] += 0.20
    if indpro_yoy is not None and indpro_yoy < 0:
        scores["recession"] += 0.20
    if hy is not None and hy > 6:
        scores["recession"] += 0.20
    if icsa_yoy is not None and icsa_yoy > 10:
        scores["recession"] += 0.10
    if umcsent_yoy is not None and umcsent_yoy < -10:
        scores["recession"] += 0.10

    # --- Early ---
    if unrate_chg is not None and unrate_chg < 0:
        scores["early"] += 0.20
    if ff_chg is not None and ff_chg < 0:
        scores["early"] += 0.20
    if t10y2y is not None and t10y2y > 1:
        scores["early"] += 0.20
    if indpro_yoy is not None and -1 < indpro_yoy < 2:
        scores["early"] += 0.20
    if hy is not None and hy < 5:
        scores["early"] += 0.10
    if umcsent_yoy is not None and umcsent_yoy > 0:
        scores["early"] += 0.10

    # --- Mid ---
    if cpi_yoy is not None and 0 < cpi_yoy < 3:
        scores["mid"] += 0.25
    if t10y2y is not None and 0.5 < t10y2y < 2:
        scores["mid"] += 0.25
    if indpro_yoy is not None and indpro_yoy > 1.5:
        scores["mid"] += 0.25
    if hy is not None and hy < 4:
        scores["mid"] += 0.15
    if unrate_chg is not None and abs(unrate_chg) < 0.15:
        scores["mid"] += 0.10

    # --- Late ---
    if cpi_yoy is not None and cpi_yoy > 3:
        scores["late"] += 0.25
    if ff_chg is not None and ff_chg > 0.5:
        scores["late"] += 0.25
    if t10y2y is not None and -0.2 < t10y2y < 0.5:
        scores["late"] += 0.25
    if unrate is not None and unrate < 4.2:
        scores["late"] += 0.15
    if umcsent_yoy is not None and umcsent_yoy > 5:
        scores["late"] += 0.10

    # Clamp to [0, 1]
    for p in scores:
        scores[p] = max(0.0, min(1.0, scores[p]))
    return scores


def detect_phase(indicators: dict) -> tuple[str, float, dict]:
    """Return (winning_phase, score, all_scores). 'uncertain' if max < 0.3."""
    scores = score_phase(indicators)
    if not scores:
        return ("uncertain", 0.0, scores)
    winner = max(scores, key=lambda k: scores[k])
    top = scores[winner]
    if top < 0.3:
        return ("uncertain", top, scores)
    return (winner, top, scores)


_SECTOR_MAP: dict[str, dict] = {
    "early": {
        "overweight": ["XLY", "XLF", "XLI", "XLB", "XLRE"],
        "underweight": ["XLU", "XLP"],
    },
    "mid": {
        "overweight": ["XLK", "XLC", "XLI"],
        "underweight": ["XLU", "XLP"],
    },
    "late": {
        "overweight": ["XLE", "XLB", "XLV", "XLP"],
        "underweight": ["XLY", "XLRE"],
    },
    "recession": {
        "overweight": ["XLP", "XLV", "XLU"],
        "underweight": ["XLF", "XLY", "XLI", "XLE"],
    },
    "uncertain": {"overweight": [], "underweight": []},
}


def phase_to_sectors(phase: str) -> dict:
    """Return classic sector tilt recommendation for a given phase."""
    return _SECTOR_MAP.get(phase, _SECTOR_MAP["uncertain"])
