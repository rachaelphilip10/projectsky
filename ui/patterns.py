"""
HazeCrop Malaysia — UI: Historical Pattern Tab

Renders the interactive monthly AOD seasonal chart and the
year-by-year comparison view.

Public API
----------
  render_patterns_idle()
  render_patterns_results(pattern_result, outlook_result, historical_years)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config.settings import DARK_LAYOUT, MONTH_LABELS, MONTH_FULL_NAMES, RISK_COLOURS


def _layout(**overrides) -> dict:
    """Return DARK_LAYOUT merged with axis/style overrides (no duplicate keys)."""
    base = dict(DARK_LAYOUT)
    for key, val in overrides.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            base[key] = {**base[key], **val}
        else:
            base[key] = val
    return base


def render_patterns_idle() -> None:
    st.markdown('<div id="patterns"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-section-label">📈 &nbsp;Historical AOD Pattern</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hc-card" style="text-align:center;padding:40px 28px;">
        <div style="font-size:32px;margin-bottom:14px;">📈</div>
        <div class="hc-card-title" style="font-size:17px;margin-bottom:10px;">Historical Pattern</div>
        <div class="hc-card-body" style="max-width:440px;margin:0 auto;">
            Run an analysis to see the multi-year monthly AOD pattern and
            seasonal risk scores for the selected state.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_patterns_results(pattern_result: dict,
                             outlook_result: dict,
                             historical_years: int) -> None:
    """Render the seasonal pattern charts."""
    st.markdown('<div id="patterns"></div>', unsafe_allow_html=True)
    st.markdown('<div class="hc-section-label">📈 &nbsp;Historical AOD Pattern</div>', unsafe_allow_html=True)

    scored_df   = pattern_result["scored_df"]
    haze_season = pattern_result["haze_season"]
    outlook     = outlook_result["outlook"]

    high_risk_months = haze_season["high_risk_months"]
    peak_month       = haze_season["peak_month"]

    # ── Tab: Seasonal Mean  |  Year Comparison ────────────────────────────────
    tab_seasonal, tab_yearly = st.tabs(["📊 Seasonal Monthly Mean", "📅 Year-by-Year Comparison"])

    with tab_seasonal:
        _render_seasonal_chart(scored_df, high_risk_months, peak_month, outlook)

    with tab_yearly:
        _render_yearly_chart(pattern_result)


def _render_seasonal_chart(scored_df: pd.DataFrame,
                            high_risk_months: list[int],
                            peak_month: int,
                            outlook: dict) -> None:
    """Monthly mean AOD bar/line chart with risk highlighting."""
    df = scored_df.copy()

    # Colour each bar by risk category
    bar_colours = []
    for _, row in df.iterrows():
        cat = row.get("Risk_Category", "Low")
        bar_colours.append(RISK_COLOURS.get(cat, "#4ade80"))

    # Build figure
    fig = go.Figure()

    # Uncertainty band (mean ± 1 std)
    valid = df.dropna(subset=["Mean_AOD", "Std_AOD"])
    if not valid.empty:
        fig.add_trace(go.Scatter(
            x=list(valid["Month"]) + list(valid["Month"])[::-1],
            y=list(valid["Mean_AOD"] + valid["Std_AOD"]) +
              list((valid["Mean_AOD"] - valid["Std_AOD"]).clip(lower=0))[::-1],
            fill="toself",
            fillcolor="rgba(34,211,238,0.07)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=True,
            name="± 1 Std Dev",
            hoverinfo="skip",
        ))

    # Mean AOD bars
    fig.add_trace(go.Bar(
        x=df["Month"],
        y=df["Mean_AOD"],
        name="Mean AOD",
        marker=dict(color=bar_colours, opacity=0.85,
                    line=dict(color="rgba(255,255,255,0.12)", width=1)),
        hovertemplate="<b>%{customdata}</b><br>Mean AOD: %{y:.3f}<extra></extra>",
        customdata=df["Month_Name"],
    ))

    # Mean AOD line overlay
    fig.add_trace(go.Scatter(
        x=df["Month"],
        y=df["Mean_AOD"],
        mode="lines+markers",
        name="Trend",
        line=dict(color="#22d3ee", width=2),
        marker=dict(size=6, color="#22d3ee", line=dict(color="#0f1117", width=1.5)),
        hoverinfo="skip",
    ))

    # Peak month annotation
    peak_row = df[df["Month"] == peak_month]
    if not peak_row.empty:
        fig.add_annotation(
            x=peak_month,
            y=float(peak_row["Mean_AOD"].iloc[0]),
            text=f"⬆ Peak: {peak_row['Month_Name'].iloc[0]}",
            showarrow=True,
            arrowhead=2,
            ax=0, ay=-40,
            font=dict(color="#fb923c", size=11, family="Inter"),
            arrowcolor="#fb923c",
        )

    # High-risk month shading
    for m in high_risk_months:
        fig.add_vrect(
            x0=m - 0.5, x1=m + 0.5,
            fillcolor="rgba(248,113,113,0.06)",
            layer="below", line_width=0,
        )

    fig.update_layout(**_layout(
        title=dict(
            text=f"Monthly AOD Seasonal Pattern — {outlook['state']}",
            font=dict(size=14, color="rgba(255,255,255,0.8)"),
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=MONTH_LABELS,
            title="Month",
        ),
        yaxis=dict(title="Mean AOD (MODIS MAIAC ~0.55 µm)"),
        height=380,
        barmode="overlay",
    ))
    st.plotly_chart(fig, use_container_width=True)

    # Risk score chart
    _render_risk_score_chart(scored_df, high_risk_months, peak_month)


def _render_risk_score_chart(scored_df: pd.DataFrame,
                              high_risk_months: list[int],
                              peak_month: int) -> None:
    """Horizontal bar chart of Seasonal Risk Scores."""
    df = scored_df.copy().sort_values("Month")
    colours = [RISK_COLOURS.get(cat, "#4ade80") for cat in df["Risk_Category"]]

    fig = go.Figure(go.Bar(
        x=df["Seasonal_Risk_Score"],
        y=df["Month_Name"],
        orientation="h",
        marker=dict(color=colours, opacity=0.8,
                    line=dict(color="rgba(255,255,255,0.1)", width=1)),
        hovertemplate="<b>%{y}</b><br>Risk Score: %{x:.1f}<extra></extra>",
    ))
    fig.add_vline(x=50, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                  annotation_text="Moderate threshold (50)")
    fig.update_layout(**_layout(
        title=dict(text="Seasonal Risk Score by Month",
                   font=dict(size=13, color="rgba(255,255,255,0.8)")),
        xaxis=dict(title="Seasonal Risk Score (0–100)", range=[0, 105]),
        yaxis=dict(autorange="reversed"),
        height=380,
    ))
    st.plotly_chart(fig, use_container_width=True)


def _render_yearly_chart(pattern_result: dict) -> None:
    """Year-by-year monthly AOD line chart."""
    pivot = pattern_result.get("yearly_pivot")
    if pivot is None or pivot.empty:
        st.info("Year-by-year data is not available for this analysis.")
        return

    fig = go.Figure()
    colours_cycle = ["#22d3ee", "#4ade80", "#fb923c", "#a78bfa",
                     "#f87171", "#fbbf24", "#818cf8", "#34d399",
                     "#f472b6", "#60a5fa"]

    for i, year in enumerate(sorted(pivot.index)):
        row = pivot.loc[year]
        colour = colours_cycle[i % len(colours_cycle)]
        fig.add_trace(go.Scatter(
            x=list(range(1, 13)),
            y=[row.get(m, None) for m in range(1, 13)],
            mode="lines+markers",
            name=str(year),
            line=dict(color=colour, width=1.8),
            marker=dict(size=5, color=colour),
            connectgaps=False,
            hovertemplate=f"<b>{year}</b> %{{customdata}}<br>AOD: %{{y:.3f}}<extra></extra>",
            customdata=MONTH_LABELS,
        ))

    fig.update_layout(**_layout(
        title=dict(text="Year-by-Year Monthly AOD Comparison",
                   font=dict(size=14, color="rgba(255,255,255,0.8)")),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=MONTH_LABELS,
            title="Month",
        ),
        yaxis=dict(title="Mean AOD"),
        height=400,
    ))
    st.plotly_chart(fig, use_container_width=True)
