import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Celestial | PnL Dashboard",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THEME / CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #0b0e13;
    --surface:   #111620;
    --border:    #1e2535;
    --accent:    #00d4a0;
    --accent2:   #4f8cff;
    --warn:      #ff6b6b;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --positive:  #00d4a0;
    --negative:  #ff6b6b;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--surface);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stDateInput label,
section[data-testid="stSidebar"] .stSlider label {
    color: var(--muted);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1rem 1.25rem;
}
div[data-testid="metric-container"] label {
    color: var(--muted) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: var(--text) !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
}

/* Section headers */
.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
    margin-top: 1.5rem;
}

.dash-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: 0.05em;
}
.dash-subtitle {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.1rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--border);
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    background: transparent;
    border: none;
    padding: 0.5rem 1.25rem;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}

/* Dataframe */
.stDataFrame {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
}

/* Plotly charts background handled via template */
.js-plotly-plot {
    border: 1px solid var(--border);
    border-radius: 4px;
}

div[data-testid="stHorizontalBlock"] > div {gap: 1rem;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY TEMPLATE
# ─────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="#111620",
    plot_bgcolor="#111620",
    font=dict(family="IBM Plex Mono, monospace", color="#e2e8f0", size=11),
    xaxis=dict(gridcolor="#1e2535", linecolor="#1e2535", zerolinecolor="#1e2535"),
    yaxis=dict(gridcolor="#1e2535", linecolor="#1e2535", zerolinecolor="#1e2535"),
    legend=dict(bgcolor="#111620", bordercolor="#1e2535", borderwidth=1),
    margin=dict(l=40, r=20, t=40, b=40),
    hovermode="x unified",
)

COLORS = {
    "Total":        "#e2e8f0",
    "Rates":        "#4f8cff",
    "Credit":       "#00d4a0",
    "Inflation":    "#f59e0b",
    "SwapSpread":   "#a78bfa",
    "Carry":        "#34d399",
    "FX":           "#fb923c",
    "Residual":     "#64748b",
    "ForwardSwap":  "#e879f9",
    "NewBusiness":  "#38bdf8",
    "RatesParallel":"#93c5fd",
    "RatesCurve":   "#6366f1",
    "RatesSlope":   "#8b5cf6",
    "RatesFly":     "#c084fc",
}

CCY_COLORS = {"Total": "#e2e8f0", "EUR": "#4f8cff", "GBP": "#00d4a0", "USD": "#fb923c"}

ISSUER_COLORS = px.colors.qualitative.Vivid

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    try:
        pnl = pd.read_excel("PnL_Master.xlsx", sheet_name="PnL by CCY")
        iss = pd.read_excel("PnL_Master.xlsx", sheet_name="Issuer PnL")
        pnl["Date"] = pd.to_datetime(pnl["Date"])
        iss["Date"] = pd.to_datetime(iss["Date"])
        return pnl, iss
    except FileNotFoundError:
        # ── DEMO DATA ──────────────────────────────────────────────────
        st.warning("⚠  PnL_Master.xlsx not found — showing synthetic demo data.", icon="⚠")
        return _make_demo_data()

def _make_demo_data():
    rng = pd.date_range("2024-09-01", periods=50, freq="B")
    pnl_types = ["Total","Rates","Credit","Inflation","SwapSpread","Carry",
                 "FX","Residual","ForwardSwap","NewBusiness",
                 "RatesParallel","RatesCurve","RatesSlope","RatesFly"]
    ccys = ["Total","EUR","GBP","USD"]
    rows = []
    np.random.seed(42)
    for d in rng:
        for pt in pnl_types:
            base = np.random.randn() * 50000
            for c in ccys:
                rows.append({"Date": d, "PnL Type": pt, "Currency": c,
                              "Value": base * np.random.uniform(0.5,1.5) * (0.3 if c!="Total" else 1)})
    pnl_df = pd.DataFrame(rows)

    issuers = ["Germany","France","Italy","Spain","Finland","Austria","ESM",
               "EU","Netherlands","Portugal","Greece","UK","US"]
    metrics = ["CreditParallel","CreditCurve","CreditPnL","Residual"]
    irows = []
    for d in rng:
        for iss in issuers:
            for m in metrics:
                irows.append({"Date": d, "Issuer": iss, "Metric": m,
                               "Value": np.random.randn() * 20000})
    iss_df = pd.DataFrame(irows)
    return pnl_df, iss_df

pnl_df, iss_df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="dash-title">◈ CELESTIAL</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-subtitle">Fixed Income PnL · Dharma AM</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("##### FILTERS")

    min_d, max_d = pnl_df["Date"].min().date(), pnl_df["Date"].max().date()
    date_range = st.date_input("Date Range", value=(min_d, max_d),
                               min_value=min_d, max_value=max_d)
    if len(date_range) == 2:
        d_start, d_end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    else:
        d_start, d_end = pd.Timestamp(min_d), pd.Timestamp(max_d)

    currency = st.selectbox("Base Currency View", ["Total","EUR","GBP","USD"])

    all_types = sorted(pnl_df["PnL Type"].unique())
    top_types = ["Total","Rates","Credit","Inflation","SwapSpread","Carry","FX","Residual"]
    selected_types = st.multiselect("PnL Types", all_types,
                                    default=[t for t in top_types if t in all_types])
    if not selected_types:
        selected_types = all_types

    all_issuers = sorted(iss_df["Issuer"].unique())
    selected_issuers = st.multiselect("Issuers", all_issuers, default=all_issuers)
    if not selected_issuers:
        selected_issuers = all_issuers

    chart_type = st.radio("Chart Style", ["Line", "Bar", "Area"], horizontal=True)

    st.markdown("---")
    n_days = (d_end - d_start).days + 1
    st.markdown(f'<span style="font-family:IBM Plex Mono;font-size:0.65rem;color:#64748b">'
                f'{pnl_df["Date"].nunique()} trading days · {n_days} calendar days</span>',
                unsafe_allow_html=True)
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────
# FILTERED DATA
# ─────────────────────────────────────────────
mask_pnl = ((pnl_df["Date"] >= d_start) & (pnl_df["Date"] <= d_end) &
            (pnl_df["PnL Type"].isin(selected_types)) &
            (pnl_df["Currency"] == currency))
fpnl = pnl_df[mask_pnl].copy()

mask_iss = ((iss_df["Date"] >= d_start) & (iss_df["Date"] <= d_end) &
            (iss_df["Issuer"].isin(selected_issuers)))
fiss = iss_df[mask_iss].copy()

# ─────────────────────────────────────────────
# HEADER KPIs
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">Performance Summary</p>', unsafe_allow_html=True)

total_pnl_series = pnl_df[(pnl_df["PnL Type"]=="Total") & (pnl_df["Currency"]==currency) &
                           (pnl_df["Date"]>=d_start) & (pnl_df["Date"]<=d_end)]

total_val = total_pnl_series["Value"].sum()
daily_avg = total_pnl_series["Value"].mean()
best_day  = total_pnl_series.groupby("Date")["Value"].sum().max() if not total_pnl_series.empty else 0
worst_day = total_pnl_series.groupby("Date")["Value"].sum().min() if not total_pnl_series.empty else 0
sharpe_proxy = (daily_avg / total_pnl_series["Value"].std()) * (252**0.5) if total_pnl_series["Value"].std() != 0 else 0

def fmt(v):
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:+.2f}M"
    if abs(v) >= 1_000:
        return f"{v/1_000:+.1f}K"
    return f"{v:+.0f}"

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total PnL", fmt(total_val))
col2.metric("Daily Avg", fmt(daily_avg))
col3.metric("Best Day", fmt(best_day))
col4.metric("Worst Day", fmt(worst_day))
col5.metric("Sharpe (ann.)", f"{sharpe_proxy:.2f}")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "  PnL Over Time  ",
    "  Currency Breakdown  ",
    "  Issuer Attribution  ",
    "  Raw Tables  "
])

# ══════════════════════════════════════════════
# TAB 1 — PnL Over Time
# ══════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-header">PnL by Type · ' + currency + '</p>', unsafe_allow_html=True)

    daily_pivot = (fpnl.groupby(["Date","PnL Type"])["Value"]
                        .sum().reset_index()
                        .pivot(index="Date", columns="PnL Type", values="Value")
                        .fillna(0).sort_index())

    # ── Main chart ────────────────────────────────
    fig = go.Figure()
    types_to_plot = [t for t in selected_types if t != "Total"]

    for i, pt in enumerate(types_to_plot):
        if pt not in daily_pivot.columns:
            continue
        color = COLORS.get(pt, "#94a3b8")
        y = daily_pivot[pt]
        if chart_type == "Line":
            fig.add_trace(go.Scatter(x=daily_pivot.index, y=y, name=pt,
                                     line=dict(color=color, width=1.5),
                                     mode="lines", hovertemplate=f"{pt}: %{{y:,.0f}}<extra></extra>"))
        elif chart_type == "Bar":
            fig.add_trace(go.Bar(x=daily_pivot.index, y=y, name=pt,
                                 marker_color=color, hovertemplate=f"{pt}: %{{y:,.0f}}<extra></extra>"))
        else:  # Area
            fig.add_trace(go.Scatter(x=daily_pivot.index, y=y, name=pt,
                                     fill="tozeroy", line=dict(color=color, width=1),
                                     fillcolor=color.replace("#", "rgba(").rstrip(")") if color.startswith("#") else color,
                                     mode="lines", opacity=0.6,
                                     hovertemplate=f"{pt}: %{{y:,.0f}}<extra></extra>"))

    # Total as bold overlay
    if "Total" in selected_types and "Total" in daily_pivot.columns:
        fig.add_trace(go.Scatter(x=daily_pivot.index, y=daily_pivot["Total"],
                                 name="Total", line=dict(color="#e2e8f0", width=2.5, dash="dot"),
                                 mode="lines", hovertemplate="Total: %{y:,.0f}<extra></extra>"))

    if chart_type == "Bar":
        fig.update_layout(barmode="relative")

    fig.update_layout(**PLOT_LAYOUT, height=380, title="Daily PnL by Type",
                      title_font=dict(size=11, color="#64748b"))
    st.plotly_chart(fig, use_container_width=True)

    # ── Cumulative PnL ────────────────────────────
    st.markdown('<p class="section-header">Cumulative PnL</p>', unsafe_allow_html=True)
    fig2 = go.Figure()
    for pt in (types_to_plot + (["Total"] if "Total" in selected_types else [])):
        if pt not in daily_pivot.columns:
            continue
        color = COLORS.get(pt, "#94a3b8")
        cum = daily_pivot[pt].cumsum()
        lw = 2.5 if pt == "Total" else 1.2
        fig2.add_trace(go.Scatter(x=cum.index, y=cum, name=pt,
                                   line=dict(color=color, width=lw),
                                   mode="lines",
                                   hovertemplate=f"{pt} cum: %{{y:,.0f}}<extra></extra>"))
    fig2.add_hline(y=0, line_color="#1e2535", line_width=1)
    fig2.update_layout(**PLOT_LAYOUT, height=320, title="Cumulative PnL by Type",
                       title_font=dict(size=11, color="#64748b"))
    st.plotly_chart(fig2, use_container_width=True)

    # ── Period summary table ───────────────────────
    st.markdown('<p class="section-header">Period Summary by Type</p>', unsafe_allow_html=True)
    if not daily_pivot.empty:
        summary = pd.DataFrame({
            "Total PnL":  daily_pivot.sum(),
            "Daily Avg":  daily_pivot.mean(),
            "Std Dev":    daily_pivot.std(),
            "Best Day":   daily_pivot.max(),
            "Worst Day":  daily_pivot.min(),
        }).round(0)
        summary = summary.sort_values("Total PnL", ascending=False)
        def _cell_color(val):
            if val > 0:
                intensity = min(val / (summary["Total PnL"].abs().max() + 1e-9), 1.0)
                g = int(80 + 120 * intensity)
                return f"rgba(0,{g},80,0.35)"
            elif val < 0:
                intensity = min(abs(val) / (summary["Total PnL"].abs().max() + 1e-9), 1.0)
                r = int(120 + 135 * intensity)
                return f"rgba({r},40,40,0.35)"
            return "rgba(30,37,53,0.5)"

        row_colors = [[_cell_color(v) for v in summary["Total PnL"]]]
        neutral = [["rgba(17,22,32,0.0)"] * len(summary)] * 4

        fig_tbl = go.Figure(go.Table(
            header=dict(
                values=["<b>PnL Type</b>"] + [f"<b>{c}</b>" for c in summary.columns],
                fill_color="#1e2535", font=dict(family="IBM Plex Mono", color="#e2e8f0", size=10),
                align="right", line_color="#0b0e13", height=28,
            ),
            cells=dict(
                values=[summary.index.tolist()] + [
                    [f"{v:,.0f}" for v in summary[col]] for col in summary.columns
                ],
                fill_color=[["rgba(17,22,32,0.6)"] * len(summary)] + row_colors + neutral,
                font=dict(family="IBM Plex Mono", color="#e2e8f0", size=10),
                align=["left"] + ["right"] * len(summary.columns),
                line_color="#0b0e13", height=24,
            ),
        ))
        fig_tbl.update_layout(**PLOT_LAYOUT, height=80 + len(summary) * 26,
                              margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_tbl, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — Currency Breakdown
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-header">PnL by Currency · All Types</p>', unsafe_allow_html=True)

    ccy_mask = ((pnl_df["Date"]>=d_start) & (pnl_df["Date"]<=d_end) &
                (pnl_df["PnL Type"].isin(selected_types)) &
                (pnl_df["Currency"] != "Total"))
    ccy_df = pnl_df[ccy_mask].copy()

    col_a, col_b = st.columns(2)

    # Left: stacked bar over time by CCY (for a selected PnL type)
    with col_a:
        drill_type = st.selectbox("Drill into PnL Type", 
                                  [t for t in selected_types if t != "Total"] or selected_types,
                                  key="ccy_drill")
        ccy_time = (ccy_df[ccy_df["PnL Type"]==drill_type]
                    .groupby(["Date","Currency"])["Value"].sum().reset_index()
                    .pivot(index="Date", columns="Currency", values="Value").fillna(0).sort_index())

        fig3 = go.Figure()
        for ccy in ["EUR","GBP","USD"]:
            if ccy in ccy_time.columns:
                fig3.add_trace(go.Bar(x=ccy_time.index, y=ccy_time[ccy],
                                      name=ccy, marker_color=CCY_COLORS[ccy],
                                      hovertemplate=f"{ccy}: %{{y:,.0f}}<extra></extra>"))
        fig3.update_layout(**PLOT_LAYOUT, barmode="relative", height=320,
                           title=f"{drill_type} PnL by Currency",
                           title_font=dict(size=11, color="#64748b"))
        st.plotly_chart(fig3, use_container_width=True)

    # Right: donut by CCY for whole period
    with col_b:
        ccy_total = ccy_df.groupby("Currency")["Value"].sum().reset_index()
        ccy_total = ccy_total[ccy_total["Value"].abs() > 0]
        fig4 = go.Figure(go.Pie(
            labels=ccy_total["Currency"],
            values=ccy_total["Value"].abs(),
            hole=0.6,
            marker=dict(colors=[CCY_COLORS.get(c,"#94a3b8") for c in ccy_total["Currency"]]),
            textfont=dict(family="IBM Plex Mono"),
            hovertemplate="%{label}: %{value:,.0f}<extra></extra>",
        ))
        fig4.update_layout(**PLOT_LAYOUT, height=320,
                           title="Currency Mix (abs PnL) — Period",
                           title_font=dict(size=11, color="#64748b"),
                           showlegend=True)
        st.plotly_chart(fig4, use_container_width=True)

    # Heatmap: PnL Type × Currency
    st.markdown('<p class="section-header">Heatmap — Type × Currency</p>', unsafe_allow_html=True)
    heat_df = (ccy_df.groupby(["PnL Type","Currency"])["Value"]
                     .sum().reset_index()
                     .pivot(index="PnL Type", columns="Currency", values="Value").fillna(0))
    fig5 = go.Figure(go.Heatmap(
        z=heat_df.values,
        x=heat_df.columns.tolist(),
        y=heat_df.index.tolist(),
        colorscale=[[0,"#ff6b6b"],[0.5,"#1e2535"],[1,"#00d4a0"]],
        zmid=0,
        text=[[f"{v:,.0f}" for v in row] for row in heat_df.values],
        texttemplate="%{text}",
        textfont=dict(family="IBM Plex Mono", size=10),
        hovertemplate="Type: %{y}<br>CCY: %{x}<br>PnL: %{z:,.0f}<extra></extra>",
        colorbar=dict(tickfont=dict(family="IBM Plex Mono", size=9)),
    ))
    fig5.update_layout(**PLOT_LAYOUT, height=420,
                       title="Period PnL — Type × Currency",
                       title_font=dict(size=11, color="#64748b"))
    st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — Issuer Attribution
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-header">Issuer Credit Attribution</p>', unsafe_allow_html=True)

    metric_sel = st.radio("Metric", ["CreditPnL","CreditParallel","CreditCurve","Residual"],
                          horizontal=True)

    iss_metric = fiss[fiss["Metric"]==metric_sel].copy()

    col_c, col_d = st.columns([3,2])

    with col_c:
        # Stacked bar over time by issuer
        iss_time = (iss_metric.groupby(["Date","Issuer"])["Value"].sum().reset_index()
                              .pivot(index="Date", columns="Issuer", values="Value").fillna(0).sort_index())

        fig6 = go.Figure()
        for i, iss in enumerate(iss_time.columns):
            fig6.add_trace(go.Bar(x=iss_time.index, y=iss_time[iss],
                                  name=iss,
                                  marker_color=ISSUER_COLORS[i % len(ISSUER_COLORS)],
                                  hovertemplate=f"{iss}: %{{y:,.0f}}<extra></extra>"))
        fig6.update_layout(**PLOT_LAYOUT, barmode="relative", height=380,
                           title=f"{metric_sel} by Issuer — Daily",
                           title_font=dict(size=11, color="#64748b"))
        st.plotly_chart(fig6, use_container_width=True)

    with col_d:
        # Period totals — horizontal bar
        iss_totals = (iss_metric.groupby("Issuer")["Value"].sum()
                                .sort_values(ascending=True).reset_index())
        colors_bar = ["#ff6b6b" if v<0 else "#00d4a0" for v in iss_totals["Value"]]
        fig7 = go.Figure(go.Bar(
            x=iss_totals["Value"], y=iss_totals["Issuer"],
            orientation="h",
            marker_color=colors_bar,
            hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
            text=[f"{v:,.0f}" for v in iss_totals["Value"]],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=9, color="#e2e8f0"),
        ))
        fig7.update_layout(**PLOT_LAYOUT, height=380,
                           title=f"Period Total {metric_sel}",
                           title_font=dict(size=11, color="#64748b"),
                           xaxis_title="", yaxis_title="")
        st.plotly_chart(fig7, use_container_width=True)

    # All metrics heatmap by issuer
    st.markdown('<p class="section-header">All Metrics · Issuer Heatmap</p>', unsafe_allow_html=True)
    all_metrics_heat = (fiss.groupby(["Issuer","Metric"])["Value"].sum().reset_index()
                            .pivot(index="Issuer", columns="Metric", values="Value").fillna(0))
    fig8 = go.Figure(go.Heatmap(
        z=all_metrics_heat.values,
        x=all_metrics_heat.columns.tolist(),
        y=all_metrics_heat.index.tolist(),
        colorscale=[[0,"#ff6b6b"],[0.5,"#111620"],[1,"#00d4a0"]],
        zmid=0,
        text=[[f"{v:,.0f}" for v in row] for row in all_metrics_heat.values],
        texttemplate="%{text}",
        textfont=dict(family="IBM Plex Mono", size=10),
        hovertemplate="Issuer: %{y}<br>Metric: %{x}<br>Value: %{z:,.0f}<extra></extra>",
        colorbar=dict(tickfont=dict(family="IBM Plex Mono", size=9)),
    ))
    fig8.update_layout(**PLOT_LAYOUT, height=480,
                       title="Issuer × Metric Heatmap — Period",
                       title_font=dict(size=11, color="#64748b"))
    st.plotly_chart(fig8, use_container_width=True)

    # Cumulative issuer PnL lines
    st.markdown('<p class="section-header">Cumulative ' + metric_sel + ' by Issuer</p>', unsafe_allow_html=True)
    fig9 = go.Figure()
    for i, iss in enumerate(iss_time.columns):
        cum = iss_time[iss].cumsum()
        fig9.add_trace(go.Scatter(x=cum.index, y=cum, name=iss,
                                   line=dict(color=ISSUER_COLORS[i % len(ISSUER_COLORS)], width=1.5),
                                   mode="lines",
                                   hovertemplate=f"{iss}: %{{y:,.0f}}<extra></extra>"))
    fig9.add_hline(y=0, line_color="#1e2535", line_width=1)
    fig9.update_layout(**PLOT_LAYOUT, height=340,
                       title=f"Cumulative {metric_sel} by Issuer",
                       title_font=dict(size=11, color="#64748b"))
    st.plotly_chart(fig9, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — Raw Tables
# ══════════════════════════════════════════════
with tab4:
    col_e, col_f = st.columns(2)
    with col_e:
        st.markdown('<p class="section-header">PnL by CCY (filtered)</p>', unsafe_allow_html=True)
        display_pnl = fpnl[["Date","PnL Type","Currency","Value"]].copy()
        display_pnl["Date"] = display_pnl["Date"].dt.strftime("%d %b %Y")
        display_pnl["Value"] = display_pnl["Value"].round(0)
        st.dataframe(display_pnl, use_container_width=True, height=500)

    with col_f:
        st.markdown('<p class="section-header">Issuer PnL (filtered)</p>', unsafe_allow_html=True)
        display_iss = fiss[["Date","Issuer","Metric","Value"]].copy()
        display_iss["Date"] = display_iss["Date"].dt.strftime("%d %b %Y")
        display_iss["Value"] = display_iss["Value"].round(0)
        st.dataframe(display_iss, use_container_width=True, height=500)

    # Download buttons
    st.markdown('<p class="section-header">Export</p>', unsafe_allow_html=True)
    col_g, col_h, _ = st.columns([1,1,3])
    with col_g:
        st.download_button("⬇ PnL CSV", fpnl.to_csv(index=False),
                           file_name="pnl_filtered.csv", mime="text/csv")
    with col_h:
        st.download_button("⬇ Issuer CSV", fiss.to_csv(index=False),
                           file_name="issuer_filtered.csv", mime="text/csv")
