import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
    --bg:       #000026;
    --surface:  #000026;
    --border:   #1a1a4a;
    --accent:   #83cceb;
    --accent2:  #31661c;
    --warn:     #c85c5c;
    --text:     #ffffff;
    --muted:    #83cceb;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #000026;
    border-right: 1px solid #1a1a4a;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stDateInput label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #ffffff !important;
    font-family: 'IBM Plex Mono', monospace;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stDateInput label {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background-color: #000026;
    border: 1px solid #1a1a4a;
    border-radius: 4px;
    padding: 1rem 1.25rem;
}
div[data-testid="metric-container"] label {
    color: #83cceb !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #ffffff !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
}

/* ── Section headers ── */
.section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.9rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #83cceb;
    border-bottom: 1px solid #1a1a4a;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
    margin-top: 1.5rem;
}
.dash-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: #ffffff;
    letter-spacing: 0.05em;
}
.dash-subtitle {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #83cceb;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.1rem;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #1a1a4a;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #83cceb;
    background: transparent;
    border: none;
    padding: 0.5rem 1.25rem;
}
.stTabs [aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 2px solid #83cceb !important;
    background: transparent !important;
}

/* ── Misc ── */
.stDataFrame { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; }
.js-plotly-plot { border: 1px solid #1a1a4a; border-radius: 4px; }
div[data-testid="stHorizontalBlock"] > div { gap: 1rem; }

/* Radio + other widget text */
.stRadio label, .stRadio div { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

# Charts: white background, black text
PLOT_LAYOUT = dict(
    paper_bgcolor="#83cceb",
    plot_bgcolor="#83cceb",
    font=dict(family="IBM Plex Mono, monospace", color="#000000", size=11),
    xaxis=dict(gridcolor="#5aaac8", linecolor="#5aaac8", zerolinecolor="#5aaac8", tickfont=dict(color="#000000")),
    yaxis=dict(gridcolor="#5aaac8", linecolor="#5aaac8", zerolinecolor="#5aaac8", tickfont=dict(color="#000000")),
    legend=dict(bgcolor="#83cceb", bordercolor="#5aaac8", borderwidth=1, font=dict(color="#000000")),    
    margin=dict(l=40, r=20, t=40, b=40),
    hovermode="x unified",
)
TABLE_LAYOUT = dict(
    paper_bgcolor="#83cceb",
    plot_bgcolor="#83cceb",
    font=dict(family="IBM Plex Mono, monospace", color="#000000", size=11),
    margin=dict(l=0, r=0, t=0, b=0),
)

# Chart series colors — readable on white
COLORS = {
    "Total":        "#000000",
    "Rates":        "#83cceb",
    "Credit":       "#31661c",
    "Inflation":    "#e08c2a",
    "SwapSpread":   "#7060a0",
    "Carry":        "#2a7a5a",
    "FX":           "#c85c2a",
    "Residual":     "#808090",
    "ForwardSwap":  "#9060b0",
    "NewBusiness":  "#3080b0",
    "RatesParallel":"#50a8d0",
    "RatesCurve":   "#4060a0",
    "RatesSlope":   "#507850",
    "RatesFly":     "#708850",
}
CCY_COLORS   = {"Total": "#000000", "EUR": "#83cceb", "GBP": "#31661c", "USD": "#c85c2a"}
RISK_COLORS  = {
    "RatesRisk":     "#83cceb",
    "BetaRatesRisk": "#50a8d0",
    "SwapSpreadRisk":"#7060a0",
    "InflationRisk": "#e08c2a",
    "FXBalance":     "#c85c2a",
    "CreditRisk":    "#31661c",
    "BetaCreditRisk":"#2a7a5a",
}
ISSUER_COLORS = [
    "#83cceb","#31661c","#e08c2a","#7060a0","#c85c2a",
    "#2a7a5a","#9060b0","#3080b0","#50a8d0","#c0603a",
    "#507850","#708850","#4060a0",
]
period_colors = {"MTD": "#83cceb", "YTD": "#31661c", "LTD": "#7060a0"}

TENORS        = ["2Y", "5Y", "10Y", "20Y", "30Y"]
CCYS          = ["EUR", "GBP", "USD"]
ISSUERS       = ["Germany","France","Italy","Spain","Finland","Austria",
                 "ESM","EU","Netherlands","Portugal","Greece","UK","US"]
TENOR_CCY_RISK = ["RatesRisk","BetaRatesRisk","SwapSpreadRisk","InflationRisk"]
ISSUER_RISK    = ["CreditRisk","BetaCreditRisk"]

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    sheets = {}
    try:
        xl = pd.ExcelFile("PnL_Master.xlsx")
        for sheet in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=sheet)
            df["Date"] = pd.to_datetime(df["Date"])
            sheets[sheet] = df
    except FileNotFoundError:
        st.warning("⚠  PnL_Master.xlsx not found — showing synthetic demo data.", icon="⚠")
        sheets = _make_demo_data()
    return sheets

def _make_demo_data():
    rng = pd.date_range("2025-02-16", periods=50, freq="B")
    np.random.seed(42)
    pnl_types = ["Total","Rates","Credit","Inflation","SwapSpread","Carry",
                 "FX","Residual","ForwardSwap","NewBusiness",
                 "RatesParallel","RatesCurve","RatesSlope","RatesFly"]
    rows = []
    for d in rng:
        for pt in pnl_types:
            base = np.random.randn() * 50000
            for c in ["Total","EUR","GBP","USD"]:
                rows.append({"Date": d, "PnL Type": pt, "Currency": c,
                             "Value": base * np.random.uniform(0.5,1.5) * (0.3 if c!="Total" else 1)})
    pnl_df = pd.DataFrame(rows)

    irows = []
    for d in rng:
        for iss in ISSUERS:
            for m in ["CreditParallel","CreditCurve","CreditPnL","Residual"]:
                irows.append({"Date": d, "Issuer": iss, "Metric": m,
                              "Value": np.random.randn() * 20000})
    iss_df = pd.DataFrame(irows)

    risk_rows = []
    for d in rng:
        for rt in TENOR_CCY_RISK:
            for dim in ["Total"] + CCYS + TENORS + [f"{t}_{c}" for t in TENORS for c in CCYS]:
                risk_rows.append({"Date": d, "Risk Type": rt, "Dimension": dim,
                                  "Value": np.random.randn() * 5000})
        for rt in ISSUER_RISK:
            for dim in ["Total"] + ISSUERS:
                risk_rows.append({"Date": d, "Risk Type": rt, "Dimension": dim,
                                  "Value": np.random.randn() * 3000})
        risk_rows.append({"Date": d, "Risk Type": "FXBalance", "Dimension": "Total",
                          "Value": np.random.randn() * 10000})
        for c in CCYS:
            risk_rows.append({"Date": d, "Risk Type": "FXBalance", "Dimension": c,
                              "Value": np.random.randn() * 4000})
    risk_df = pd.DataFrame(risk_rows)

    period_rows = []
    instruments = ["Total","Bonds","Futures","Swaps","FX","Inflation"]
    for d in rng:
        for period in ["MTD","YTD","LTD"]:
            base = np.random.randn() * 200000
            for inst in instruments:
                period_rows.append({"Date": d, "Period": period, "Instrument": inst,
                                    "Value": base * np.random.uniform(0.5,1.5) * (0.3 if inst!="Total" else 1)})
    period_df = pd.DataFrame(period_rows)

    return {"PnL by CCY": pnl_df, "Issuer PnL": iss_df, "Risk": risk_df, "MTD YTD LTD": period_df}

sheets    = load_data()
pnl_df    = sheets.get("PnL by CCY",  pd.DataFrame(columns=["Date","PnL Type","Currency","Value"]))
iss_df    = sheets.get("Issuer PnL",  pd.DataFrame(columns=["Date","Issuer","Metric","Value"]))
risk_df   = sheets.get("Risk",         pd.DataFrame(columns=["Date","Risk Type","Dimension","Value"]))
period_df = sheets.get("MTD YTD LTD", pd.DataFrame(columns=["Date","Period","Instrument","Value"]))

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="dash-title">◈ CELESTIAL</div>', unsafe_allow_html=True)
    st.markdown('<div class="dash-subtitle">Fixed Income PnL · Dharma AM</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("##### FILTERS")

    min_d         = pnl_df["Date"].min().date() if not pnl_df.empty else pd.Timestamp("2025-02-16").date()
    max_d         = pnl_df["Date"].max().date() if not pnl_df.empty else pd.Timestamp("today").date()
    default_start = max(min_d, pd.Timestamp("2025-02-16").date())
    date_range    = st.date_input("Date Range", value=(default_start, max_d), min_value=min_d, max_value=max_d)
    if len(date_range) == 2:
        d_start, d_end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    else:
        d_start, d_end = pd.Timestamp(min_d), pd.Timestamp(max_d)

    currency = st.selectbox("Base Currency View", ["Total","EUR","GBP","USD"])

    all_types  = sorted(pnl_df["PnL Type"].unique()) if not pnl_df.empty else []
    top_types  = ["Total","Rates","Credit","Inflation","SwapSpread","Carry","FX","Residual"]
    selected_types = st.multiselect("PnL Types", all_types,
                                    default=[t for t in top_types if t in all_types])
    if not selected_types:
        selected_types = all_types

    all_issuers = sorted(iss_df["Issuer"].unique()) if not iss_df.empty else ISSUERS
    selected_issuers = st.multiselect("Issuers", all_issuers, default=all_issuers)
    if not selected_issuers:
        selected_issuers = all_issuers

    chart_type = st.radio("Chart Style", ["Line","Bar","Area"], horizontal=True)

    st.markdown("---")
    n_days = (d_end - d_start).days + 1
    st.markdown(f'<span style="font-family:IBM Plex Mono;font-size:0.65rem;color:#83cceb">'
                f'{pnl_df["Date"].nunique()} trading days · {n_days} calendar days</span>',
                unsafe_allow_html=True)
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────
# FILTERED DATA
# ─────────────────────────────────────────────
fpnl = pnl_df[
    (pnl_df["Date"] >= d_start) & (pnl_df["Date"] <= d_end) &
    (pnl_df["PnL Type"].isin(selected_types)) & (pnl_df["Currency"] == currency)
].copy()

fiss = iss_df[
    (iss_df["Date"] >= d_start) & (iss_df["Date"] <= d_end) &
    (iss_df["Issuer"].isin(selected_issuers))
].copy()

frisk = risk_df[
    (risk_df["Date"] >= d_start) & (risk_df["Date"] <= d_end)
].copy()

fperiod = period_df[
    (period_df["Date"] >= d_start) & (period_df["Date"] <= d_end)
].copy()

# ─────────────────────────────────────────────
# HEADER KPIs
# ─────────────────────────────────────────────
st.markdown('<p class="section-header">Performance Summary</p>', unsafe_allow_html=True)

total_series = pnl_df[
    (pnl_df["PnL Type"] == "Total") & (pnl_df["Currency"] == currency) &
    (pnl_df["Date"] >= d_start) & (pnl_df["Date"] <= d_end)
]
total_val = total_series["Value"].sum()
daily_avg = total_series["Value"].mean()
best_day  = total_series.groupby("Date")["Value"].sum().max() if not total_series.empty else 0
worst_day = total_series.groupby("Date")["Value"].sum().min() if not total_series.empty else 0
sharpe    = (daily_avg / total_series["Value"].std() * 252**0.5) if total_series["Value"].std() != 0 else 0

def fmt(v):
    if abs(v) >= 1_000_000: return f"{v/1_000_000:+.2f}M"
    if abs(v) >= 1_000:     return f"{v/1_000:+.1f}K"
    return f"{v:+.0f}"

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Total PnL",    fmt(total_val))
c2.metric("Daily Avg",    fmt(daily_avg))
c3.metric("Best Day",     fmt(best_day))
c4.metric("Worst Day",    fmt(worst_day))
c5.metric("Sharpe (ann)", f"{sharpe:.2f}")

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
HEATMAP_SCALE = [[0,"#c85c2a"],[0.5,"#ffffff"],[1,"#31661c"]]
TBL_HEADER_BG = "#000026"
TBL_HEADER_FG = "#ffffff"
TBL_CELL_BG   = "#f8f8fb"
TBL_LINE      = "#d0d0d8"

def pos_color(val, mx):
    intensity = min(val / (mx + 1e-9), 1.0)
    g = int(80 + 100 * intensity)
    return f"rgba(49,102,28,{0.2 + 0.4*intensity:.2f})"

def neg_color(val, mx):
    intensity = min(abs(val) / (mx + 1e-9), 1.0)
    return f"rgba(200,92,42,{0.2 + 0.4*intensity:.2f})"

def cell_color(val, mx):
    if val > 0:   return pos_color(val, mx)
    elif val < 0: return neg_color(val, mx)
    return "rgba(248,248,251,1)"

def pnl_summary_table(summary):
    mx = summary["Total PnL"].abs().max()
    row_colors = [[cell_color(v, mx) for v in summary["Total PnL"]]]
    neutral    = [["rgba(248,248,251,1)"] * len(summary)] * (len(summary.columns) - 1)
    fig = go.Figure(go.Table(
        header=dict(
            values=["<b>Type</b>"] + [f"<b>{c}</b>" for c in summary.columns],
            fill_color=TBL_HEADER_BG,
            font=dict(family="IBM Plex Mono", color=TBL_HEADER_FG, size=10),
            align="right", line_color=TBL_LINE, height=28,
        ),
        cells=dict(
            values=[summary.index.tolist()] + [[f"{v:,.0f}" for v in summary[c]] for c in summary.columns],
            fill_color=[["rgba(248,248,251,1)"] * len(summary)] + row_colors + neutral,
            font=dict(family="IBM Plex Mono", color="#000000", size=10),
            align=["left"] + ["right"] * len(summary.columns),
            line_color=TBL_LINE, height=24,
        ),
    ))
    fig.update_layout(**TABLE_LAYOUT, height=80 + len(summary) * 26)
    return fig

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "  PnL Over Time  ",
    "  Currency Breakdown  ",
    "  Issuer Attribution  ",
    "  Risk  ",
    "  MTD / YTD / LTD  ",
    "  Raw Tables  ",
])

# ══════════════════════════════════════════════
# TAB 1 — PnL Over Time
# ══════════════════════════════════════════════
with tab1:
    st.markdown(f'<p class="section-header">PnL by Type · {currency}</p>', unsafe_allow_html=True)

    daily_pivot = (fpnl.groupby(["Date","PnL Type"])["Value"].sum().reset_index()
                       .pivot(index="Date", columns="PnL Type", values="Value").fillna(0).sort_index())

    fig = go.Figure()
    for pt in [t for t in selected_types if t != "Total"]:
        if pt not in daily_pivot.columns: continue
        color = COLORS.get(pt, "#606070")
        y = daily_pivot[pt]
        if chart_type == "Line":
            fig.add_trace(go.Scatter(x=daily_pivot.index, y=y, name=pt,
                                     line=dict(color=color, width=1.5), mode="lines",
                                     hovertemplate=f"{pt}: %{{y:,.0f}}<extra></extra>"))
        elif chart_type == "Bar":
            fig.add_trace(go.Bar(x=daily_pivot.index, y=y, name=pt, marker_color=color,
                                 hovertemplate=f"{pt}: %{{y:,.0f}}<extra></extra>"))
        else:
            fig.add_trace(go.Scatter(x=daily_pivot.index, y=y, name=pt, fill="tozeroy",
                                     line=dict(color=color, width=1), mode="lines", opacity=0.6,
                                     hovertemplate=f"{pt}: %{{y:,.0f}}<extra></extra>"))
    if "Total" in selected_types and "Total" in daily_pivot.columns:
        fig.add_trace(go.Scatter(x=daily_pivot.index, y=daily_pivot["Total"], name="Total",
                                 line=dict(color="#000000", width=2.5, dash="dot"), mode="lines",
                                 hovertemplate="Total: %{y:,.0f}<extra></extra>"))
    if chart_type == "Bar": fig.update_layout(barmode="relative")
    fig.update_layout(**PLOT_LAYOUT, height=380, title="Daily PnL by Type",
                      title_font=dict(size=11, color="#606070"))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<p class="section-header">Cumulative PnL</p>', unsafe_allow_html=True)
    fig2 = go.Figure()
    for pt in selected_types:
        if pt not in daily_pivot.columns: continue
        cum = daily_pivot[pt].cumsum()
        fig2.add_trace(go.Scatter(x=cum.index, y=cum, name=pt,
                                  line=dict(color=COLORS.get(pt,"#606070"),
                                            width=2.5 if pt=="Total" else 1.2),
                                  mode="lines", hovertemplate=f"{pt}: %{{y:,.0f}}<extra></extra>"))
    fig2.add_hline(y=0, line_color="#3a8aaa", line_width=1)
    fig2.update_layout(**PLOT_LAYOUT, height=320, title="Cumulative PnL by Type",
                       title_font=dict(size=11, color="#606070"))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-header">Period Summary by Type</p>', unsafe_allow_html=True)
    if not daily_pivot.empty:
        summary = pd.DataFrame({
            "Total PnL": daily_pivot.sum(), "Daily Avg": daily_pivot.mean(),
            "Std Dev": daily_pivot.std(), "Best Day": daily_pivot.max(), "Worst Day": daily_pivot.min(),
        }).round(0).sort_values("Total PnL", ascending=False)
        st.plotly_chart(pnl_summary_table(summary), use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — Currency Breakdown
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-header">PnL by Currency · All Types</p>', unsafe_allow_html=True)
    ccy_df = pnl_df[
        (pnl_df["Date"] >= d_start) & (pnl_df["Date"] <= d_end) &
        (pnl_df["PnL Type"].isin(selected_types)) & (pnl_df["Currency"] != "Total")
    ].copy()

    col_a, col_b = st.columns(2)
    with col_a:
        drill_type = st.selectbox("Drill into PnL Type",
                                  [t for t in selected_types if t != "Total"] or selected_types,
                                  key="ccy_drill")
        ccy_time = (ccy_df[ccy_df["PnL Type"] == drill_type]
                    .groupby(["Date","Currency"])["Value"].sum().reset_index()
                    .pivot(index="Date", columns="Currency", values="Value").fillna(0).sort_index())
        fig3 = go.Figure()
        for ccy in ["EUR","GBP","USD"]:
            if ccy in ccy_time.columns:
                fig3.add_trace(go.Bar(x=ccy_time.index, y=ccy_time[ccy], name=ccy,
                                      marker_color=CCY_COLORS[ccy],
                                      hovertemplate=f"{ccy}: %{{y:,.0f}}<extra></extra>"))
        fig3.update_layout(**PLOT_LAYOUT, barmode="relative", height=320,
                           title=f"{drill_type} PnL by Currency",
                           title_font=dict(size=11, color="#606070"))
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        ccy_total = ccy_df.groupby("Currency")["Value"].sum().reset_index()
        ccy_total = ccy_total[ccy_total["Value"].abs() > 0]
        fig4 = go.Figure(go.Pie(
            labels=ccy_total["Currency"], values=ccy_total["Value"].abs(), hole=0.6,
            marker=dict(colors=[CCY_COLORS.get(c,"#606070") for c in ccy_total["Currency"]]),
            textfont=dict(family="IBM Plex Mono", color="#000000"),
            hovertemplate="%{label}: %{value:,.0f}<extra></extra>",
        ))
        fig4.update_layout(**PLOT_LAYOUT, height=320, title="Currency Mix (abs PnL) — Period",
                           title_font=dict(size=11, color="#606070"), showlegend=True)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<p class="section-header">Heatmap — Type × Currency</p>', unsafe_allow_html=True)
    heat_df = (ccy_df.groupby(["PnL Type","Currency"])["Value"].sum().reset_index()
               .pivot(index="PnL Type", columns="Currency", values="Value").fillna(0))
    fig5 = go.Figure(go.Heatmap(
        z=heat_df.values, x=heat_df.columns.tolist(), y=heat_df.index.tolist(),
        colorscale=HEATMAP_SCALE, zmid=0,
        text=[[f"{v:,.0f}" for v in row] for row in heat_df.values],
        texttemplate="%{text}", textfont=dict(family="IBM Plex Mono", size=10, color="#000000"),
        hovertemplate="Type: %{y}<br>CCY: %{x}<br>PnL: %{z:,.0f}<extra></extra>",
        colorbar=dict(tickfont=dict(family="IBM Plex Mono", size=9, color="#000000")),
    ))
    fig5.update_layout(**PLOT_LAYOUT, height=420, title="Period PnL — Type × Currency",
                       title_font=dict(size=11, color="#606070"))
    st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3 — Issuer Attribution
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-header">Issuer Credit Attribution</p>', unsafe_allow_html=True)
    metric_sel = st.radio("Metric", ["CreditPnL","CreditParallel","CreditCurve","Residual"], horizontal=True)
    iss_metric = fiss[fiss["Metric"] == metric_sel].copy()

    col_c, col_d = st.columns([3,2])
    with col_c:
        iss_time = (iss_metric.groupby(["Date","Issuer"])["Value"].sum().reset_index()
                    .pivot(index="Date", columns="Issuer", values="Value").fillna(0).sort_index())
        fig6 = go.Figure()
        for i, iss in enumerate(iss_time.columns):
            fig6.add_trace(go.Bar(x=iss_time.index, y=iss_time[iss], name=iss,
                                  marker_color=ISSUER_COLORS[i % len(ISSUER_COLORS)],
                                  hovertemplate=f"{iss}: %{{y:,.0f}}<extra></extra>"))
        fig6.update_layout(**PLOT_LAYOUT, barmode="relative", height=380,
                           title=f"{metric_sel} by Issuer — Daily",
                           title_font=dict(size=11, color="#606070"))
        st.plotly_chart(fig6, use_container_width=True)

    with col_d:
        iss_totals = (iss_metric.groupby("Issuer")["Value"].sum()
                      .sort_values(ascending=True).reset_index())
        fig7 = go.Figure(go.Bar(
            x=iss_totals["Value"], y=iss_totals["Issuer"], orientation="h",
            marker_color=["#c85c2a" if v < 0 else "#31661c" for v in iss_totals["Value"]],
            hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
            text=[f"{v:,.0f}" for v in iss_totals["Value"]],
            textposition="outside", textfont=dict(family="IBM Plex Mono", size=9, color="#000000"),
        ))
        fig7.update_layout(**PLOT_LAYOUT, height=380, title=f"Period Total {metric_sel}",
                           title_font=dict(size=11, color="#606070"))
        st.plotly_chart(fig7, use_container_width=True)

    st.markdown('<p class="section-header">All Metrics · Issuer Heatmap</p>', unsafe_allow_html=True)
    all_heat = (fiss.groupby(["Issuer","Metric"])["Value"].sum().reset_index()
                .pivot(index="Issuer", columns="Metric", values="Value").fillna(0))
    fig8 = go.Figure(go.Heatmap(
        z=all_heat.values, x=all_heat.columns.tolist(), y=all_heat.index.tolist(),
        colorscale=HEATMAP_SCALE, zmid=0,
        text=[[f"{v:,.0f}" for v in row] for row in all_heat.values],
        texttemplate="%{text}", textfont=dict(family="IBM Plex Mono", size=10, color="#000000"),
        hovertemplate="Issuer: %{y}<br>Metric: %{x}<br>Value: %{z:,.0f}<extra></extra>",
        colorbar=dict(tickfont=dict(family="IBM Plex Mono", size=9, color="#000000")),
    ))
    fig8.update_layout(**PLOT_LAYOUT, height=480, title="Issuer × Metric Heatmap — Period",
                       title_font=dict(size=11, color="#606070"))
    st.plotly_chart(fig8, use_container_width=True)

    st.markdown(f'<p class="section-header">Cumulative {metric_sel} by Issuer</p>', unsafe_allow_html=True)
    fig9 = go.Figure()
    for i, iss in enumerate(iss_time.columns):
        cum = iss_time[iss].cumsum()
        fig9.add_trace(go.Scatter(x=cum.index, y=cum, name=iss,
                                  line=dict(color=ISSUER_COLORS[i % len(ISSUER_COLORS)], width=1.5),
                                  mode="lines", hovertemplate=f"{iss}: %{{y:,.0f}}<extra></extra>"))
    fig9.add_hline(y=0, line_color="#d0d0d8", line_width=1)
    fig9.update_layout(**PLOT_LAYOUT, height=340, title=f"Cumulative {metric_sel} by Issuer",
                       title_font=dict(size=11, color="#606070"))
    st.plotly_chart(fig9, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — RISK
# ══════════════════════════════════════════════
with tab4:
    if frisk.empty:
        st.info("No risk data available for the selected period.")
    else:
        risk_type_sel = st.selectbox("Risk Type",
                                     TENOR_CCY_RISK + ISSUER_RISK + ["FXBalance"],
                                     key="risk_type_sel")
        latest_date  = frisk["Date"].max()
        is_tenor_ccy = risk_type_sel in TENOR_CCY_RISK
        is_issuer    = risk_type_sel in ISSUER_RISK
        rdata        = frisk[frisk["Risk Type"] == risk_type_sel]

        if is_tenor_ccy:
            st.markdown(f'<p class="section-header">Tenor × CCY Matrix · {risk_type_sel} · {latest_date.strftime("%d %b %Y")}</p>',
                        unsafe_allow_html=True)
            latest = rdata[rdata["Date"] == latest_date]
            matrix_rows = []
            for t in TENORS:
                row = {"Tenor": t}
                for c in ["Total"] + CCYS:
                    key = f"{t}_{c}" if c != "Total" else t
                    val_row = latest[latest["Dimension"] == key]["Value"]
                    row[c] = val_row.values[0] if not val_row.empty else 0
                matrix_rows.append(row)
            tot_row = {"Tenor": "Total"}
            for c in ["Total"] + CCYS:
                val_row = latest[latest["Dimension"] == c]["Value"]
                tot_row[c] = val_row.values[0] if not val_row.empty else 0
            matrix_rows.append(tot_row)
            matrix_df = pd.DataFrame(matrix_rows).set_index("Tenor")
            col_order  = ["Total"] + CCYS
            fig_heat = go.Figure(go.Heatmap(
                z=matrix_df[col_order].values, x=col_order, y=matrix_df.index.tolist(),
                colorscale=HEATMAP_SCALE, zmid=0,
                text=[[f"{v:,.0f}" for v in row] for row in matrix_df[col_order].values],
                texttemplate="%{text}", textfont=dict(family="IBM Plex Mono", size=11, color="#000000"),
                hovertemplate="Tenor: %{y}<br>CCY: %{x}<br>Value: %{z:,.0f}<extra></extra>",
                colorbar=dict(tickfont=dict(family="IBM Plex Mono", size=9, color="#000000")),
            ))
            fig_heat.update_layout(**PLOT_LAYOUT, height=320,
                                   title=f"{risk_type_sel} — Tenor × CCY",
                                   title_font=dict(size=11, color="#606070"))
            st.plotly_chart(fig_heat, use_container_width=True)

        if is_issuer:
            st.markdown(f'<p class="section-header">{risk_type_sel} by Issuer · {latest_date.strftime("%d %b %Y")}</p>',
                        unsafe_allow_html=True)
            latest = rdata[rdata["Date"] == latest_date]
            iss_latest = (latest[latest["Dimension"].isin(ISSUERS)]
                          .groupby("Dimension")["Value"].sum()
                          .sort_values(ascending=True).reset_index())
            fig_iss = go.Figure(go.Bar(
                x=iss_latest["Value"], y=iss_latest["Dimension"], orientation="h",
                marker_color=["#c85c2a" if v < 0 else "#31661c" for v in iss_latest["Value"]],
                text=[f"{v:,.0f}" for v in iss_latest["Value"]],
                textposition="outside", textfont=dict(family="IBM Plex Mono", size=9, color="#000000"),
                hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
            ))
            fig_iss.update_layout(**PLOT_LAYOUT, height=400,
                                  title=f"{risk_type_sel} by Issuer",
                                  title_font=dict(size=11, color="#606070"))
            st.plotly_chart(fig_iss, use_container_width=True)

        st.markdown(f'<p class="section-header">{risk_type_sel} Over Time</p>', unsafe_allow_html=True)
        if is_tenor_ccy:
            dim_options  = ["Total"] + CCYS + TENORS
            default_dims = ["Total"] + CCYS
        elif is_issuer:
            dim_options  = ["Total"] + ISSUERS
            default_dims = ["Total"]
        else:
            dim_options  = ["Total"] + CCYS
            default_dims = ["Total"] + CCYS

        dims_sel = st.multiselect("Dimensions to plot", dim_options,
                                  default=default_dims, key="risk_dims")
        risk_ts = (rdata[rdata["Dimension"].isin(dims_sel)]
                   .groupby(["Date","Dimension"])["Value"].sum().reset_index()
                   .pivot(index="Date", columns="Dimension", values="Value").fillna(0).sort_index())
        fig_ts = go.Figure()
        for i, dim in enumerate(dims_sel):
            if dim not in risk_ts.columns: continue
            color = CCY_COLORS.get(dim, ISSUER_COLORS[i % len(ISSUER_COLORS)])
            fig_ts.add_trace(go.Scatter(x=risk_ts.index, y=risk_ts[dim], name=dim,
                                        line=dict(color=color, width=1.8), mode="lines",
                                        hovertemplate=f"{dim}: %{{y:,.0f}}<extra></extra>"))
        fig_ts.add_hline(y=0, line_color="#d0d0d8", line_width=1)
        fig_ts.update_layout(**PLOT_LAYOUT, height=360,
                             title=f"{risk_type_sel} — Daily Positions",
                             title_font=dict(size=11, color="#606070"))
        st.plotly_chart(fig_ts, use_container_width=True)

        st.markdown('<p class="section-header">All Risk Types · Total Position · Latest Day</p>',
                    unsafe_allow_html=True)
        all_latest = frisk[(frisk["Date"] == latest_date) & (frisk["Dimension"] == "Total")]
        all_totals = all_latest.groupby("Risk Type")["Value"].sum().sort_values(ascending=True).reset_index()
        fig_all = go.Figure(go.Bar(
            x=all_totals["Value"], y=all_totals["Risk Type"], orientation="h",
            marker_color=[RISK_COLORS.get(r,"#606070") for r in all_totals["Risk Type"]],
            text=[f"{v:,.0f}" for v in all_totals["Value"]],
            textposition="outside", textfont=dict(family="IBM Plex Mono", size=9, color="#000000"),
            hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
        ))
        fig_all.update_layout(**PLOT_LAYOUT, height=320,
                              title=f"Total Risk by Type — {latest_date.strftime('%d %b %Y')}",
                              title_font=dict(size=11, color="#606070"))
        st.plotly_chart(fig_all, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 — MTD / YTD / LTD
# ══════════════════════════════════════════════
with tab5:
    if fperiod.empty:
        st.info("No MTD/YTD/LTD data available for the selected period.")
    else:
        all_instruments = sorted(fperiod["Instrument"].unique())
        latest_p_date   = fperiod["Date"].max()

        st.markdown(f'<p class="section-header">Latest Snapshot · {latest_p_date.strftime("%d %b %Y")}</p>',
                    unsafe_allow_html=True)
        snap = (fperiod[fperiod["Date"] == latest_p_date]
                .groupby(["Period","Instrument"])["Value"].sum().reset_index()
                .pivot(index="Instrument", columns="Period", values="Value").fillna(0))
        col_order_p = [p for p in ["MTD","YTD","LTD"] if p in snap.columns]
        snap = snap[col_order_p]
        if "Total" in snap.index:
            snap = pd.concat([snap.loc[["Total"]], snap.drop("Total")])

        def _p_color(val, col_vals):
            mx = max(abs(col_vals.max()), abs(col_vals.min()), 1)
            if val > 0:   return pos_color(val, mx)
            elif val < 0: return neg_color(val, mx)
            return "rgba(248,248,251,1)"

        cell_colors = [["rgba(248,248,251,1)"] * len(snap)]
        for col in col_order_p:
            cell_colors.append([_p_color(v, snap[col]) for v in snap[col]])

        fig_snap = go.Figure(go.Table(
            header=dict(
                values=["<b>Instrument</b>"] + [f"<b>{c}</b>" for c in col_order_p],
                fill_color=TBL_HEADER_BG,
                font=dict(family="IBM Plex Mono", color=TBL_HEADER_FG, size=10),
                align="right", line_color=TBL_LINE, height=28,
            ),
            cells=dict(
                values=[snap.index.tolist()] + [[f"{v:,.0f}" for v in snap[c]] for c in col_order_p],
                fill_color=cell_colors,
                font=dict(family="IBM Plex Mono", color="#000000", size=10),
                align=["left"] + ["right"] * len(col_order_p),
                line_color=TBL_LINE, height=24,
            ),
        ))
        fig_snap.update_layout(**TABLE_LAYOUT, height=80 + len(snap) * 26)
        st.plotly_chart(fig_snap, use_container_width=True)

        st.markdown('<p class="section-header">Instrument Breakdown · Latest</p>', unsafe_allow_html=True)
        snap_reset = snap.reset_index()
        fig_bar = go.Figure()
        for p in col_order_p:
            fig_bar.add_trace(go.Bar(
                x=snap_reset["Instrument"], y=snap_reset[p], name=p,
                marker_color=period_colors.get(p, "#606070"),
                hovertemplate=f"{p}: %{{y:,.0f}}<extra></extra>",
            ))
        fig_bar.update_layout(**PLOT_LAYOUT, barmode="group", height=360,
                              title="MTD / YTD / LTD by Instrument — Latest",
                              title_font=dict(size=11, color="#606070"))
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown('<p class="section-header">How Periods Have Evolved Over Time</p>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            period_ts_sel = st.selectbox("Period", col_order_p, key="period_ts")
        with col_p2:
            inst_ts_sel = st.multiselect("Instruments", all_instruments,
                                         default=all_instruments[:min(5, len(all_instruments))],
                                         key="inst_ts")
        ts_data = (fperiod[(fperiod["Period"] == period_ts_sel) &
                            (fperiod["Instrument"].isin(inst_ts_sel))]
                   .groupby(["Date","Instrument"])["Value"].sum().reset_index()
                   .pivot(index="Date", columns="Instrument", values="Value").fillna(0).sort_index())
        fig_evo = go.Figure()
        for i, inst in enumerate(inst_ts_sel):
            if inst not in ts_data.columns: continue
            fig_evo.add_trace(go.Scatter(x=ts_data.index, y=ts_data[inst], name=inst,
                                         line=dict(color=ISSUER_COLORS[i % len(ISSUER_COLORS)],
                                                   width=2.5 if inst=="Total" else 1.5),
                                         mode="lines",
                                         hovertemplate=f"{inst}: %{{y:,.0f}}<extra></extra>"))
        fig_evo.add_hline(y=0, line_color="#d0d0d8", line_width=1)
        fig_evo.update_layout(**PLOT_LAYOUT, height=360,
                              title=f"{period_ts_sel} by Instrument — Daily Evolution",
                              title_font=dict(size=11, color="#606070"))
        st.plotly_chart(fig_evo, use_container_width=True)

        st.markdown('<p class="section-header">All Periods · Single Instrument</p>', unsafe_allow_html=True)
        inst_single = st.selectbox("Instrument", all_instruments, key="inst_single")
        single_data = (fperiod[fperiod["Instrument"] == inst_single]
                       .groupby(["Date","Period"])["Value"].sum().reset_index()
                       .pivot(index="Date", columns="Period", values="Value").fillna(0).sort_index())
        fig_single = go.Figure()
        for p in col_order_p:
            if p not in single_data.columns: continue
            fig_single.add_trace(go.Scatter(x=single_data.index, y=single_data[p], name=p,
                                            line=dict(color=period_colors.get(p,"#606070"), width=1.8),
                                            mode="lines",
                                            hovertemplate=f"{p}: %{{y:,.0f}}<extra></extra>"))
        fig_single.add_hline(y=0, line_color="#d0d0d8", line_width=1)
        fig_single.update_layout(**PLOT_LAYOUT, height=320,
                                 title=f"MTD / YTD / LTD — {inst_single}",
                                 title_font=dict(size=11, color="#606070"))
        st.plotly_chart(fig_single, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 6 — Raw Tables
# ══════════════════════════════════════════════
with tab6:
    raw_tab_sel = st.radio("Table", ["PnL by CCY","Issuer PnL","Risk","MTD YTD LTD"], horizontal=True)

    if raw_tab_sel == "PnL by CCY":
        d = fpnl.copy(); d["Date"] = d["Date"].dt.strftime("%d %b %Y"); d["Value"] = d["Value"].round(0)
        st.dataframe(d, use_container_width=True, height=550)
        st.download_button("⬇ Download CSV", d.to_csv(index=False), file_name="pnl_ccy.csv", mime="text/csv")
    elif raw_tab_sel == "Issuer PnL":
        d = fiss.copy(); d["Date"] = d["Date"].dt.strftime("%d %b %Y"); d["Value"] = d["Value"].round(0)
        st.dataframe(d, use_container_width=True, height=550)
        st.download_button("⬇ Download CSV", d.to_csv(index=False), file_name="issuer_pnl.csv", mime="text/csv")
    elif raw_tab_sel == "Risk":
        d = frisk.copy(); d["Date"] = d["Date"].dt.strftime("%d %b %Y"); d["Value"] = d["Value"].round(2)
        st.dataframe(d, use_container_width=True, height=550)
        st.download_button("⬇ Download CSV", d.to_csv(index=False), file_name="risk.csv", mime="text/csv")
    else:
        d = fperiod.copy(); d["Date"] = d["Date"].dt.strftime("%d %b %Y"); d["Value"] = d["Value"].round(0)
        st.dataframe(d, use_container_width=True, height=550)
        st.download_button("⬇ Download CSV", d.to_csv(index=False), file_name="mtd_ytd_ltd.csv", mime="text/csv")
