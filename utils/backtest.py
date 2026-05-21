"""Monthly top-N sectors momentum backtest with benchmark comparison.

Strategy: at each month-end, rank non-benchmark tickers by trailing
``lookback_months`` return; hold the top ``n`` equal-weighted until next
rebalance. Transaction cost model: ``cost_bps/10000 * turnover_fraction``
deducted from the upcoming month's return, where ``turnover_fraction`` is
half the L1 distance between consecutive weight vectors.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

_PRIMARY = "#2563eb"
_GRAY = "#888888"


def monthly_resample(prices: pd.DataFrame) -> pd.DataFrame:
    """Return month-end prices."""
    if prices is None or prices.empty:
        return pd.DataFrame()
    return prices.resample("ME").last().dropna(how="all")


def _summary_stats(monthly_ret: pd.Series, equity: pd.Series) -> dict:
    if monthly_ret.empty or equity.empty:
        return {"cagr": 0.0, "vol_ann": 0.0, "sharpe": 0.0,
                "max_drawdown": 0.0, "hit_rate": 0.0, "total_return": 0.0}
    n_months = len(monthly_ret)
    total_return = float(equity.iloc[-1] - 1.0)
    years = n_months / 12.0
    cagr = float(equity.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else 0.0
    vol_ann = float(monthly_ret.std(ddof=0) * np.sqrt(12)) if n_months > 1 else 0.0
    sharpe = float(cagr / vol_ann) if vol_ann > 1e-9 else 0.0
    dd = equity / equity.cummax() - 1.0
    max_dd = float(dd.min()) if not dd.empty else 0.0
    hit_rate = float((monthly_ret > 0).mean())
    return {"cagr": cagr, "vol_ann": vol_ann, "sharpe": sharpe,
            "max_drawdown": max_dd, "hit_rate": hit_rate,
            "total_return": total_return}


def _empty_result() -> dict:
    cols = ["strategy", "benchmark"]
    return {
        "equity": pd.DataFrame(columns=cols),
        "monthly_returns": pd.DataFrame(columns=cols),
        "stats": {"strategy": _summary_stats(pd.Series(dtype=float), pd.Series(dtype=float)),
                  "benchmark": _summary_stats(pd.Series(dtype=float), pd.Series(dtype=float))},
        "holdings": pd.DataFrame(),
    }


def top_n_momentum_backtest(
    prices: pd.DataFrame,
    benchmark: str = "SPY",
    n: int = 3,
    lookback_months: int = 6,
    cost_bps: float = 5.0,
) -> dict:
    """Run a monthly top-N momentum backtest vs a buy-and-hold benchmark.

    Cost model: deduct ``cost_bps/10000 * turnover`` from the month's return,
    where ``turnover = 0.5 * sum(|w_t - w_{t-1}|)`` (one-way turnover).
    """
    if prices is None or prices.empty or benchmark not in prices.columns:
        return _empty_result()

    monthly = monthly_resample(prices)
    if monthly.shape[0] <= lookback_months + 1:
        return _empty_result()

    sector_cols = [c for c in monthly.columns if c != benchmark]
    if not sector_cols:
        return _empty_result()

    monthly_ret_all = monthly.pct_change()
    bench_ret = monthly_ret_all[benchmark]

    dates = monthly.index
    cost = cost_bps / 10000.0

    holdings_rows: dict[pd.Timestamp, pd.Series] = {}
    strat_returns: dict[pd.Timestamp, float] = {}
    prev_weights = pd.Series(0.0, index=sector_cols)

    for i in range(lookback_months, len(dates) - 1):
        t = dates[i]
        t_next = dates[i + 1]
        window_start = dates[i - lookback_months]
        lookback_ret = (monthly.loc[t, sector_cols] /
                        monthly.loc[window_start, sector_cols] - 1.0).dropna()
        if lookback_ret.empty:
            continue
        top = lookback_ret.sort_values(ascending=False).head(n).index.tolist()
        if not top:
            continue
        w = pd.Series(0.0, index=sector_cols)
        w.loc[top] = 1.0 / len(top)
        holdings_rows[t] = w

        next_returns = monthly_ret_all.loc[t_next, top].fillna(0.0)
        gross = float(next_returns.mean())
        turnover = float(0.5 * (w - prev_weights).abs().sum())
        net = gross - cost * turnover
        strat_returns[t_next] = net
        prev_weights = w

    if not strat_returns:
        return _empty_result()

    strat_ret = pd.Series(strat_returns).sort_index()
    bench_ret_aligned = bench_ret.loc[strat_ret.index].fillna(0.0)

    monthly_returns = pd.DataFrame({
        "strategy": strat_ret,
        "benchmark": bench_ret_aligned,
    })
    equity = (1.0 + monthly_returns).cumprod()

    holdings = pd.DataFrame(holdings_rows).T.reindex(columns=sector_cols).fillna(0.0)
    holdings.index.name = "Date"

    stats = {
        "strategy": _summary_stats(monthly_returns["strategy"], equity["strategy"]),
        "benchmark": _summary_stats(monthly_returns["benchmark"], equity["benchmark"]),
    }

    return {
        "equity": equity,
        "monthly_returns": monthly_returns,
        "stats": stats,
        "holdings": holdings,
    }


def _mobile_layout(fig: go.Figure, title: str, ylabel: str = "", xlabel: str = "תאריך") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center"),
        xaxis=dict(title=xlabel, showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(title=ylabel, showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        height=420, dragmode="pan",
        margin=dict(l=40, r=20, t=60, b=40),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        modebar=dict(remove=["lasso2d", "select2d", "autoScale2d", "zoomIn2d", "zoomOut2d"]),
    )
    return fig


def equity_curve_figure(equity: pd.DataFrame) -> go.Figure:
    """Two-line equity curve: strategy vs benchmark."""
    fig = go.Figure()
    if equity is None or equity.empty:
        return _mobile_layout(fig, "עקומת הון: אסטרטגיה מול בנצ'מארק", "ערך תיק (התחלה=1)")
    if "strategy" in equity.columns:
        fig.add_trace(go.Scatter(
            x=equity.index, y=equity["strategy"], mode="lines",
            name="אסטרטגיה", line=dict(color=_PRIMARY, width=2.2),
        ))
    if "benchmark" in equity.columns:
        fig.add_trace(go.Scatter(
            x=equity.index, y=equity["benchmark"], mode="lines",
            name="בנצ'מארק", line=dict(color=_GRAY, width=1.8, dash="dot"),
        ))
    return _mobile_layout(fig, "עקומת הון: אסטרטגיה מול בנצ'מארק", "ערך תיק (התחלה=1)")


def drawdown_figure(equity: pd.DataFrame) -> go.Figure:
    """Filled drawdown area chart for strategy and benchmark."""
    fig = go.Figure()
    if equity is None or equity.empty:
        return _mobile_layout(fig, "Drawdown", "Drawdown")
    for col, color, label in [
        ("strategy", _PRIMARY, "אסטרטגיה"),
        ("benchmark", _GRAY, "בנצ'מארק"),
    ]:
        if col not in equity.columns:
            continue
        dd = equity[col] / equity[col].cummax() - 1.0
        fig.add_trace(go.Scatter(
            x=dd.index, y=dd, mode="lines", name=label,
            line=dict(color=color, width=1.5), fill="tozeroy",
            fillcolor=color.replace(")", ", 0.18)").replace("rgb", "rgba")
            if color.startswith("rgb") else (
                "rgba(37, 99, 235, 0.18)" if color == _PRIMARY else "rgba(136, 136, 136, 0.18)"
            ),
        ))
    fig.update_yaxes(tickformat=".0%")
    return _mobile_layout(fig, "Drawdown", "Drawdown")


def holdings_heatmap(holdings: pd.DataFrame, sector_names: dict[str, str]) -> go.Figure:
    """Heatmap of monthly holdings (rows: tickers, cols: dates)."""
    fig = go.Figure()
    if holdings is None or holdings.empty:
        return _mobile_layout(fig, "אחזקות לפי חודש", "מגזר", "תאריך")
    mat = holdings.T
    y_labels = [
        f"{t} · {sector_names[t]}" if t in sector_names else t
        for t in mat.index
    ]
    colorscale = [
        [0.0, "rgba(240, 240, 245, 1)"],
        [0.001, "rgba(220, 230, 250, 1)"],
        [1.0, _PRIMARY],
    ]
    fig.add_trace(go.Heatmap(
        z=mat.values, x=mat.columns, y=y_labels,
        colorscale=colorscale, zmin=0.0,
        zmax=float(mat.values.max()) if mat.size and mat.values.max() > 0 else 1.0,
        showscale=False, xgap=1, ygap=1,
        hovertemplate="%{y}<br>%{x|%Y-%m}<br>משקל: %{z:.2f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="אחזקות לפי חודש", x=0.5, xanchor="center"),
        xaxis=dict(title="תאריך"),
        yaxis=dict(title="מגזר", autorange="reversed"),
        height=max(420, 24 * len(y_labels) + 120),
        dragmode="pan",
        margin=dict(l=120, r=20, t=60, b=40),
        plot_bgcolor="white", paper_bgcolor="white",
        modebar=dict(remove=["lasso2d", "select2d", "autoScale2d"]),
    )
    return fig
