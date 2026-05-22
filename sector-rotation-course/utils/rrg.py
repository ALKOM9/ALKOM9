"""Relative Rotation Graph (RRG) computation and visualization.

A simplified academic approximation of the Bloomberg-style RRG used to chart
sector rotation against a benchmark (e.g. SPDR sector ETFs vs SPY).
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

QUADRANTS = ("leading", "improving", "weakening", "lagging")

_QUADRANT_HE: dict[str, str] = {
    "leading": "🟢 מובילים",
    "improving": "🔵 משתפרים",
    "weakening": "🟡 נחלשים",
    "lagging": "🔴 פיגרים",
}

_QUADRANT_COLOR: dict[str, str] = {
    "leading": "rgba(0, 180, 90, 0.10)",
    "improving": "rgba(60, 120, 220, 0.10)",
    "weakening": "rgba(230, 190, 40, 0.12)",
    "lagging": "rgba(220, 60, 60, 0.10)",
}


def compute_rrg(
    prices: pd.DataFrame,
    benchmark: str,
    lookback: int = 14,
    smoothing: int = 10,
) -> pd.DataFrame:
    """Compute RS-Ratio and RS-Momentum for each non-benchmark ticker.

    Returns a DataFrame with MultiIndex (Date, Ticker) and columns
    ``['rs_ratio', 'rs_momentum']``.
    """
    if benchmark not in prices.columns:
        raise ValueError(f"benchmark '{benchmark}' not in prices columns")

    bench = prices[benchmark]
    frames: list[pd.DataFrame] = []

    for ticker in prices.columns:
        if ticker == benchmark:
            continue
        ratio = prices[ticker] / bench
        rs_ratio_raw = 100 * ratio / ratio.rolling(lookback).mean()
        rs_ratio = rs_ratio_raw.ewm(span=smoothing, adjust=False).mean()
        rs_momentum = 100 * (rs_ratio / rs_ratio.shift(4))

        df = pd.DataFrame(
            {"rs_ratio": rs_ratio, "rs_momentum": rs_momentum}
        ).dropna()
        df["Ticker"] = ticker
        df.index.name = "Date"
        frames.append(df.set_index("Ticker", append=True))

    if not frames:
        return pd.DataFrame(
            columns=["rs_ratio", "rs_momentum"],
            index=pd.MultiIndex.from_arrays([[], []], names=["Date", "Ticker"]),
        )

    return pd.concat(frames).sort_index()


def latest_rrg_point(rrg: pd.DataFrame, ticker: str) -> tuple[float, float]:
    """Return (rs_ratio, rs_momentum) for the most recent date of ``ticker``."""
    sub = rrg.xs(ticker, level="Ticker")
    if sub.empty:
        raise ValueError(f"no RRG data for ticker '{ticker}'")
    row = sub.iloc[-1]
    return float(row["rs_ratio"]), float(row["rs_momentum"])


def rrg_tail(
    rrg: pd.DataFrame, ticker: str, tail_length: int = 8
) -> pd.DataFrame:
    """Return last ``tail_length`` points for ``ticker`` (Date-indexed)."""
    sub = rrg.xs(ticker, level="Ticker")
    return sub.tail(tail_length)


def quadrant(rs_ratio: float, rs_momentum: float) -> str:
    """Classify a point into one of the four RRG quadrants."""
    if rs_ratio >= 100 and rs_momentum >= 100:
        return "leading"
    if rs_ratio < 100 and rs_momentum >= 100:
        return "improving"
    if rs_ratio >= 100 and rs_momentum < 100:
        return "weakening"
    return "lagging"


def quadrant_label_he(quad: str) -> str:
    """Return Hebrew label with emoji for a quadrant key."""
    return _QUADRANT_HE.get(quad, quad)


def _axis_range(rrg: pd.DataFrame, tickers: list[str], pad: float = 2.0) -> tuple[float, float]:
    available = set(rrg.index.get_level_values("Ticker"))
    vals: list[float] = []
    for t in tickers:
        if t in available:
            sub = rrg.xs(t, level="Ticker")
            vals.extend(sub["rs_ratio"].tolist() + sub["rs_momentum"].tolist())
    if not vals:
        return 90.0, 110.0
    half = max(abs(100 - (min(vals) - pad)), abs((max(vals) + pad) - 100), 5.0)
    return 100 - half, 100 + half


def plot_rrg(
    rrg: pd.DataFrame,
    tickers: list[str],
    sector_names: dict[str, str],
    tail_length: int = 8,
) -> go.Figure:
    """Build a Plotly RRG scatter figure for the given tickers."""
    fig = go.Figure()
    lo, hi = _axis_range(rrg, tickers)

    # Quadrant background shading.
    for quad, x0, x1, y0, y1 in [("leading", 100, hi, 100, hi),
                                  ("weakening", 100, hi, lo, 100),
                                  ("lagging", lo, 100, lo, 100),
                                  ("improving", lo, 100, 100, hi)]:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                      fillcolor=_QUADRANT_COLOR[quad], line_width=0, layer="below")

    # Crosshair at (100, 100).
    fig.add_hline(y=100, line_width=1, line_dash="dot", line_color="#888")
    fig.add_vline(x=100, line_width=1, line_dash="dot", line_color="#888")

    for ticker in tickers:
        if ticker not in rrg.index.get_level_values("Ticker"):
            continue
        tail = rrg_tail(rrg, ticker, tail_length=tail_length)
        if tail.empty:
            continue
        xs = tail["rs_ratio"].tolist()
        ys = tail["rs_momentum"].tolist()
        last_quad = quadrant(xs[-1], ys[-1])
        label = sector_names.get(ticker, ticker)
        sizes = [5] * (len(xs) - 1) + [14]
        hover = [
            f"<b>{ticker}</b> {label}<br>"
            f"RS-Ratio: {x:.2f}<br>RS-Mom: {y:.2f}<br>"
            f"רובע: {quadrant_label_he(quadrant(x, y))}"
            for x, y in zip(xs, ys)
        ]
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys, mode="lines+markers+text",
                name=f"{ticker} {label}",
                text=[""] * (len(xs) - 1) + [ticker],
                textposition="top center",
                textfont=dict(size=12),
                marker=dict(size=sizes, line=dict(width=1, color="#222")),
                line=dict(width=1.5),
                hovertext=hover, hoverinfo="text",
                customdata=[last_quad] * len(xs),
            )
        )

    fig.update_layout(
        title=dict(text="גרף סיבוב מגזרים (RRG)", x=0.5, xanchor="center"),
        xaxis=dict(
            title="JdK RS-Ratio (כוח יחסי)", range=[lo, hi],
            zeroline=False, showgrid=True, gridcolor="rgba(0,0,0,0.05)",
        ),
        yaxis=dict(
            title="JdK RS-Momentum (מומנטום)", range=[lo, hi],
            zeroline=False, showgrid=True, gridcolor="rgba(0,0,0,0.05)",
            scaleanchor="x", scaleratio=1,
        ),
        height=600, showlegend=False, dragmode="pan",
        margin=dict(l=40, r=20, t=60, b=40),
        plot_bgcolor="white", paper_bgcolor="white",
        modebar=dict(remove=["lasso2d", "select2d", "autoScale2d"]),
    )

    corners = [("leading", hi, hi, "right", "top"),
               ("weakening", hi, lo, "right", "bottom"),
               ("lagging", lo, lo, "left", "bottom"),
               ("improving", lo, hi, "left", "top")]
    for quad, x, y, xa, ya in corners:
        fig.add_annotation(x=x, y=y, text=quadrant_label_he(quad), showarrow=False,
                           xanchor=xa, yanchor=ya, font=dict(size=12, color="#444"))
    return fig
