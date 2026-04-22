import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Celestial · PnL",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DESIGN SYSTEM
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & Root ── */
:root {
    --bg0:      #0a0a0f;
    --bg1:      #0f0f17;
    --bg2:      #14141f;
    --bg3:      #1c1c2e;
    --border:   #232338;
    --border2:  #2e2e4a;
    --accent:   #e8b84b;
    --accent2:  #4be8a0;
    --danger:   #e84b4b;
    --text0:    #ffffff;
    --text1:    #c8c8e0;
    --text2:    #7878a0;
    --text3:    #4a4a6a;
    --mono:     'Space Mono', monospace;
    --sans:     'DM Sans', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--sans);
    background-color: var(--bg0) !important;
    color: var(--text1);
}

/* ── App background ── */
.stApp { background-color: var(--bg0); }
.main .block-container { padding: 1.5rem 2rem 2rem; max-width: 100%; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: var(--bg1) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { padding: 1.5rem 1.25rem; }

/* Sidebar text */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] .stMarkdown {
    color: var(--text1) !important;
    font-family: var(--mono) !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stDateInput label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.6rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--text2) !important;
}

/* Sidebar inputs */
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: var(--bg2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 3px !important;
    color: var(--text0) !important;
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
}

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background-color: var(--bg1);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent);
    border-radius: 2px;
    padding: 1rem 1.2rem 0.9rem;
    transition: border-color 0.2s;
}
div[data-testid="metric-container"]:hover {
    border-color: var(--border2);
    border-top-color: var(--accent);
}
div[data-testid="metric-container"] label {
    color: var(--text2) !important;
    font-family: var(--mono) !important;
    font-size: 0.58rem !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    font-weight: 700 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: var(--mono) !important;
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    color: var(--text0) !important;
    letter-spacing: -0.02em !important;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-family: var(--mono) !important;
    font-size: 0.68rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--border);
    background: transparent;
    padding: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--mono);
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text2);
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 0.6rem 1.4rem;
    margin: 0;
    transition: color 0.15s;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text1); }
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }

/* ── Section headers ── */
.sh {
    font-family: var(--mono);
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text2);
    padding-bottom: 0.5rem;
    margin-bottom: 1.2rem;
    margin-top: 1.8rem;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.sh::before {
    content: '';
    display: inline-block;
    width: 12px;
    height: 2px;
    background: var(--accent);
}

/* ── Chart wrapper ── */
.js-plotly-plot {
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
}

/* ── Dataframe ── */
.stDataFrame {
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    border: 1px solid var(--border) !important;
}

/* ── Buttons ── */
.stButton button {
    background: transparent !important;
    border: 1px solid var(--border2) !important;
    color: var(--text2) !important;
    font-family: var(--mono) !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    padding: 0.4rem 0.9rem !important;
    transition: all 0.15s !important;
}
.stButton button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* ── Selectbox / Multiselect ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background-color: var(--bg2) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 2px !important;
    color: var(--text0) !important;
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
}

/* ── Radio ── */
.stRadio label { color: var(--text1) !important; font-family: var(--mono) !important; font-size: 0.72rem !important; }
.stRadio div { color: var(--text1) !important; }

/* ── Download button ── */
.stDownloadButton button {
    background: transparent !important;
    border: 1px solid var(--border2) !important;
    color: var(--text2) !important;
    font-family: var(--mono) !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
.stDownloadButton button:hover { border-color: var(--accent) !important; color: var(--accent) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg1); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--text3); }

/* ── Warning ── */
.stWarning { background: rgba(232,184,75,0.08) !important; border: 1px solid rgba(232,184,75,0.2) !important; border-radius: 2px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DESIGN TOKENS — DARK CHART THEME
# ─────────────────────────────────────────────
BG0   = "#0a0a0f"
BG1   = "#0f0f17"
BG2   = "#14141f"
BG3   = "#1c1c2e"
BORD  = "#232338"
BORD2 = "#2e2e4a"
GRID  = "#1a1a2e"

ACCENT  = "#e8b84b"   # amber
GREEN   = "#4be896"
RED     = "#e84b4b"
BLUE    = "#4b9be8"
PURPLE  = "#9b6be8"
TEAL    = "#4be8d4"
ORANGE  = "#e87c4b"
SLATE   = "#6b78a0"

TEXT0 = "#ffffff"
TEXT1 = "#c8c8e0"
TEXT2 = "#7878a0"

PLOT_LAYOUT = dict(
    paper_bgcolor=BG1,
    plot_bgcolor=BG2,
    font=dict(family="Space Mono, monospace", color=TEXT2, size=10),
    xaxis=dict(
        gridcolor=GRID, linecolor=BORD2, zerolinecolor=BORD2,
        tickfont=dict(color=TEXT2, size=9), ticklen=0,
        showgrid=True, zeroline=False,
    ),
    yaxis=dict(
        gridcolor=GRID, linecolor=BORD2, zerolinecolor=BORD2,
        tickfont=dict(color=TEXT2, size=9), ticklen=0,
        showgrid=True, zeroline=True, zerolinewidth=1,
    ),
    legend=dict(
        bgcolor="rgba(15,15,23,0.9)",
        bordercolor=BORD2,
        borderwidth=1,
        font=dict(color=TEXT1, size=9),
        itemsizing="constant",
    ),
    margin=dict(l=48, r=16, t=36, b=36),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor=BG3,
        bordercolor=BORD2,
        font=dict(family="Space Mono, monospace", color=TEXT0, size=10),
    ),
)

TABLE_LAYOUT = dict(
    paper_bgcolor=BG1,
    plot_bgcolor=BG1,
    font=dict(family="Space Mono, monospace", color=TEXT1, size=10),
    margin=dict(l=0, r=0, t=0, b=0),
)

# ─────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────
COLORS = {
    "Total":         TEXT0,
    "Rates":         BLUE,
    "Credit":        GREEN,
    "Inflation":     ORANGE,
    "SwapSpread":    PURPLE,
    "Carry":         TEAL,
    "FX":            ACCENT,
    "Residual":      SLATE,
    "ForwardSwap":   "#c84be8",
    "NewBusiness":   "#4be8d4",
    "RatesParallel": "#6bb8e8",
    "RatesCurve":    "#4b68e8",
    "RatesSlope":    "#68b88a",
    "RatesFly":      "#a8c858",
}
CCY_COLORS    = {"Total": TEXT0, "EUR": BLUE, "GBP": GREEN, "USD": ACCENT}
PERIOD_COLORS = {"MTD": BLUE, "YTD": GREEN, "LTD": ACCENT}
RISK_COLORS   = {
    "RatesRisk": BLUE, "BetaRatesRisk": "#6bb8e8",
    "SwapSpreadRisk": PURPLE, "InflationRisk": ORANGE,
    "FXBalance": ACCENT, "CreditRisk": GREEN, "BetaCreditRisk": TEAL,
}
ISSUER_PALETTE = [BLUE, GREEN, ACCENT, PURPLE, ORANGE, TEAL, "#c84be8",
                  "#e84b9b", "#6bb8e8", "#c88848", "#68b88a", "#a8c858", "#4b68e8"]

TENORS         = ["2Y","5Y","10Y","20Y","30Y"]
CCYS           = ["EUR","GBP","USD"]
ISSUERS        = ["Germany","France","Italy","Spain","Finland","Austria",
                  "ESM","EU","Netherlands","Portugal","Greece","UK","US"]
TENOR_CCY_RISK = ["RatesRisk","BetaRatesRisk","SwapSpreadRisk","InflationRisk"]
ISSUER_RISK    = ["CreditRisk","BetaCreditRisk"]

HEATMAP_SCALE  = [[0, RED], [0.5, BG3], [1, GREEN]]

TBL_HDR_BG = BG0
TBL_HDR_FG = TEXT1
TBL_CELL_A = BG2
TBL_CELL_B = "#111118"
TBL_LINE   = BORD

# ─────────────────────────────────────────────
# DATA
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
        st.warning("⚠  PnL_Master.xlsx not found — showing synthetic demo data.")
        sheets = _demo()
    return sheets

def _demo():
    rng  = pd.date_range("2025-02-16", periods=50, freq="B")
    np.random.seed(42)
    types = ["Total","Rates","Credit","Inflation","SwapSpread","Carry",
             "FX","Residual","ForwardSwap","NewBusiness",
             "RatesParallel","RatesCurve","RatesSlope","RatesFly"]
    rows = []
    for d in rng:
        for pt in types:
            base = np.random.randn() * 50000
            for c in ["Total","EUR","GBP","USD"]:
                rows.append({"Date":d,"PnL Type":pt,"Currency":c,
                             "Value":base*np.random.uniform(0.5,1.5)*(0.3 if c!="Total" else 1)})
    pnl = pd.DataFrame(rows)

    irows = []
    for d in rng:
        for iss in ISSUERS:
            for m in ["CreditParallel","CreditCurve","CreditPnL","Residual"]:
                irows.append({"Date":d,"Issuer":iss,"Metric":m,"Value":np.random.randn()*20000})
    iss = pd.DataFrame(irows)

    rrows = []
    for d in rng:
        for rt in TENOR_CCY_RISK:
            for dim in ["Total"]+CCYS+TENORS+[f"{t}_{c}" for t in TENORS for c in CCYS]:
                rrows.append({"Date":d,"Risk Type":rt,"Dimension":dim,"Value":np.random.randn()*5000})
        for rt in ISSUER_RISK:
            for dim in ["Total"]+ISSUERS:
                rrows.append({"Date":d,"Risk Type":rt,"Dimension":dim,"Value":np.random.randn()*3000})
        rrows.append({"Date":d,"Risk Type":"FXBalance","Dimension":"Total","Value":np.random.randn()*10000})
        for c in CCYS:
            rrows.append({"Date":d,"Risk Type":"FXBalance","Dimension":c,"Value":np.random.randn()*4000})
    risk = pd.DataFrame(rrows)

    prows = []
    insts = ["Total","Bonds","Futures","Swaps","FX","Inflation"]
    for d in rng:
        for period in ["MTD","YTD","LTD"]:
            base = np.random.randn()*200000
            for inst in insts:
                prows.append({"Date":d,"Period":period,"Instrument":inst,
                              "Value":base*np.random.uniform(0.5,1.5)*(0.3 if inst!="Total" else 1)})
    per = pd.DataFrame(prows)
    return {"PnL by CCY":pnl,"Issuer PnL":iss,"Risk":risk,"MTD YTD LTD":per}

sheets    = load_data()
pnl_df    = sheets.get("PnL by CCY",  pd.DataFrame(columns=["Date","PnL Type","Currency","Value"]))
iss_df    = sheets.get("Issuer PnL",  pd.DataFrame(columns=["Date","Issuer","Metric","Value"]))
risk_df   = sheets.get("Risk",         pd.DataFrame(columns=["Date","Risk Type","Dimension","Value"]))
period_df = sheets.get("MTD YTD LTD", pd.DataFrame(columns=["Date","Period","Instrument","Value"]))

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # Wordmark
    st.markdown("""
    <div style="margin-bottom:2rem">
      <div style="font-family:var(--mono);font-size:1rem;font-weight:700;
                  color:#ffffff;letter-spacing:0.06em">◈ CELESTIAL</div>
      <div style="font-family:var(--mono);font-size:0.55rem;color:var(--text2);
                  letter-spacing:0.18em;text-transform:uppercase;margin-top:0.2rem">
        Fixed Income PnL · Dharma AM
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sh">Date Range</div>', unsafe_allow_html=True)
    min_d  = pnl_df["Date"].min().date() if not pnl_df.empty else pd.Timestamp("2025-02-16").date()
    max_d  = pnl_df["Date"].max().date() if not pnl_df.empty else pd.Timestamp("today").date()
    d0     = max(min_d, pd.Timestamp("2025-02-16").date())
    dr     = st.date_input("", value=(d0, max_d), min_value=min_d, max_value=max_d, label_visibility="collapsed")
    d_start, d_end = (pd.Timestamp(dr[0]), pd.Timestamp(dr[1])) if len(dr)==2 else (pd.Timestamp(min_d), pd.Timestamp(max_d))

    st.markdown('<div class="sh">Display</div>', unsafe_allow_html=True)
    currency    = st.selectbox("Base Currency", ["Total","EUR","GBP","USD"])
    chart_type  = st.radio("Chart Style", ["Line","Bar","Area"], horizontal=True)

    st.markdown('<div class="sh">PnL Types</div>', unsafe_allow_html=True)
    all_types     = sorted(pnl_df["PnL Type"].unique()) if not pnl_df.empty else []
    top_types     = ["Total","Rates","Credit","Inflation","SwapSpread","Carry","FX","Residual"]
    selected_types= st.multiselect("", all_types,
                                   default=[t for t in top_types if t in all_types],
                                   label_visibility="collapsed")
    if not selected_types: selected_types = all_types

    st.markdown('<div class="sh">Issuers</div>', unsafe_allow_html=True)
    all_issuers     = sorted(iss_df["Issuer"].unique()) if not iss_df.empty else ISSUERS
    selected_issuers= st.multiselect("", all_issuers, default=all_issuers, label_visibility="collapsed")
    if not selected_issuers: selected_issuers = all_issuers

    st.markdown("---")
    n_days = (d_end - d_start).days + 1
    st.markdown(f"""
    <div style="font-family:var(--mono);font-size:0.58rem;color:var(--text2);line-height:1.8">
      <span style="color:var(--accent)">{pnl_df['Date'].nunique()}</span> trading days<br>
      <span style="color:var(--accent)">{n_days}</span> calendar days
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺  Refresh"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────
# FILTERED DATA
# ─────────────────────────────────────────────
fpnl = pnl_df[
    (pnl_df["Date"]>=d_start)&(pnl_df["Date"]<=d_end)&
    (pnl_df["PnL Type"].isin(selected_types))&(pnl_df["Currency"]==currency)
].copy()

fiss = iss_df[
    (iss_df["Date"]>=d_start)&(iss_df["Date"]<=d_end)&
    (iss_df["Issuer"].isin(selected_issuers))
].copy()

frisk  = risk_df[(risk_df["Date"]>=d_start)&(risk_df["Date"]<=d_end)].copy()
fperiod= period_df[(period_df["Date"]>=d_start)&(period_df["Date"]<=d_end)].copy()

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
ts = pnl_df[(pnl_df["PnL Type"]=="Total")&(pnl_df["Currency"]==currency)&
            (pnl_df["Date"]>=d_start)&(pnl_df["Date"]<=d_end)]

total_val = ts["Value"].sum()
daily_avg = ts["Value"].mean()
best_day  = ts.groupby("Date")["Value"].sum().max() if not ts.empty else 0
worst_day = ts.groupby("Date")["Value"].sum().min() if not ts.empty else 0
sharpe    = (daily_avg/ts["Value"].std()*252**0.5) if ts["Value"].std()!=0 else 0

def fmt(v):
    if abs(v)>=1e6: return f"{v/1e6:+.2f}M"
    if abs(v)>=1e3: return f"{v/1e3:+.1f}K"
    return f"{v:+.0f}"

# Page header
st.markdown(f"""
<div style="display:flex;align-items:baseline;gap:1rem;margin-bottom:0.2rem">
  <span style="font-family:var(--mono);font-size:1.35rem;font-weight:700;
               color:#ffffff;letter-spacing:-0.01em">Performance Summary</span>
  <span style="font-family:var(--mono);font-size:0.6rem;color:var(--text2);
               letter-spacing:0.15em;text-transform:uppercase">
    {currency} · {d_start.strftime('%d %b %y')} – {d_end.strftime('%d %b %y')}
  </span>
</div>
<div style="height:1px;background:var(--border);margin-bottom:1.2rem"></div>
""", unsafe_allow_html=True)

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Total PnL",    fmt(total_val))
c2.metric("Daily Avg",    fmt(daily_avg))
c3.metric("Best Day",     fmt(best_day))
c4.metric("Worst Day",    fmt(worst_day))
c5.metric("Sharpe (ann)", f"{sharpe:.2f}")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def sh(label):
    st.markdown(f'<div class="sh">{label}</div>', unsafe_allow_html=True)

def pos_c(v, mx): i=min(v/(mx+1e-9),1.0); return f"rgba(75,232,150,{0.08+0.22*i:.2f})"
def neg_c(v, mx): i=min(abs(v)/(mx+1e-9),1.0); return f"rgba(232,75,75,{0.08+0.22*i:.2f})"
def cell_c(v, mx):
    if v>0:   return pos_c(v,mx)
    if v<0:   return neg_c(v,mx)
    return f"rgba(20,20,31,1)"

def summary_table(df):
    mx = df["Total PnL"].abs().max()
    fig = go.Figure(go.Table(
        header=dict(
            values=["<b>TYPE</b>"]+[f"<b>{c.upper()}</b>" for c in df.columns],
            fill_color=TBL_HDR_BG,
            font=dict(family="Space Mono", color=TEXT2, size=9),
            align=["left"]+["right"]*len(df.columns),
            line_color=BORD, height=26,
        ),
        cells=dict(
            values=[df.index.tolist()]+[[f"{v:,.0f}" for v in df[c]] for c in df.columns],
            fill_color=[[TBL_CELL_A if i%2==0 else TBL_CELL_B for i in range(len(df))],
                        [cell_c(v,mx) for v in df["Total PnL"]]] +
                       [[TBL_CELL_A if i%2==0 else TBL_CELL_B for i in range(len(df))]*(len(df.columns)-1)],
            font=dict(family="Space Mono", color=TEXT1, size=9),
            align=["left"]+["right"]*len(df.columns),
            line_color=BORD, height=22,
        ),
    ))
    fig.update_layout(**TABLE_LAYOUT, height=72+len(df)*24)
    return fig

def apply_dark(fig, **kwargs):
    layout = {**PLOT_LAYOUT, **kwargs}
    fig.update_layout(**layout)
    return fig

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "PnL Over Time","Currency Breakdown","Issuer Attribution","Risk","MTD / YTD / LTD","Raw Tables"
])

# ══════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════
with tab1:
    sh(f"Daily PnL by Type · {currency}")
    daily_pivot = (fpnl.groupby(["Date","PnL Type"])["Value"].sum().reset_index()
                       .pivot(index="Date",columns="PnL Type",values="Value").fillna(0).sort_index())

    fig = go.Figure()
    for pt in [t for t in selected_types if t!="Total"]:
        if pt not in daily_pivot.columns: continue
        col = COLORS.get(pt,"#606070")
        y   = daily_pivot[pt]
        if chart_type=="Line":
            fig.add_trace(go.Scatter(x=daily_pivot.index,y=y,name=pt,
                mode="lines",line=dict(color=col,width=1.4),
                hovertemplate=f"{pt}: %{{y:,.0f}}<extra></extra>"))
        elif chart_type=="Bar":
            fig.add_trace(go.Bar(x=daily_pivot.index,y=y,name=pt,marker_color=col,
                hovertemplate=f"{pt}: %{{y:,.0f}}<extra></extra>"))
        else:
            fig.add_trace(go.Scatter(x=daily_pivot.index,y=y,name=pt,fill="tozeroy",
                mode="lines",line=dict(color=col,width=1),opacity=0.5,
                hovertemplate=f"{pt}: %{{y:,.0f}}<extra></extra>"))
    if "Total" in selected_types and "Total" in daily_pivot.columns:
        fig.add_trace(go.Scatter(x=daily_pivot.index,y=daily_pivot["Total"],name="Total",
            mode="lines",line=dict(color=TEXT0,width=2,dash="dot"),
            hovertemplate="Total: %{y:,.0f}<extra></extra>"))
    if chart_type=="Bar": fig.update_layout(barmode="relative")
    apply_dark(fig, height=380, title=dict(text="Daily PnL", font=dict(size=11,color=TEXT2)))
    st.plotly_chart(fig, use_container_width=True)

    sh("Cumulative PnL")
    fig2 = go.Figure()
    for pt in selected_types:
        if pt not in daily_pivot.columns: continue
        cum = daily_pivot[pt].cumsum()
        fig2.add_trace(go.Scatter(x=cum.index,y=cum,name=pt,mode="lines",
            line=dict(color=COLORS.get(pt,"#606070"),width=2.2 if pt=="Total" else 1.2),
            hovertemplate=f"{pt}: %{{y:,.0f}}<extra></extra>"))
    fig2.add_hline(y=0, line_color=BORD2, line_width=1)
    apply_dark(fig2, height=300, title=dict(text="Cumulative PnL by Type", font=dict(size=11,color=TEXT2)))
    st.plotly_chart(fig2, use_container_width=True)

    sh("Period Summary")
    if not daily_pivot.empty:
        summary = pd.DataFrame({
            "Total PnL":daily_pivot.sum(), "Daily Avg":daily_pivot.mean(),
            "Std Dev":daily_pivot.std(), "Best Day":daily_pivot.max(), "Worst Day":daily_pivot.min(),
        }).round(0).sort_values("Total PnL", ascending=False)
        st.plotly_chart(summary_table(summary), use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2
# ══════════════════════════════════════════════
with tab2:
    sh("PnL by Currency")
    ccy_df = pnl_df[
        (pnl_df["Date"]>=d_start)&(pnl_df["Date"]<=d_end)&
        (pnl_df["PnL Type"].isin(selected_types))&(pnl_df["Currency"]!="Total")
    ].copy()

    col_a,col_b = st.columns(2)
    with col_a:
        drill = st.selectbox("Drill into Type",[t for t in selected_types if t!="Total"] or selected_types,key="ccy_d")
        ccy_t = (ccy_df[ccy_df["PnL Type"]==drill]
                 .groupby(["Date","Currency"])["Value"].sum().reset_index()
                 .pivot(index="Date",columns="Currency",values="Value").fillna(0).sort_index())
        fig3 = go.Figure()
        for ccy in ["EUR","GBP","USD"]:
            if ccy in ccy_t.columns:
                fig3.add_trace(go.Bar(x=ccy_t.index,y=ccy_t[ccy],name=ccy,
                    marker_color=CCY_COLORS[ccy],hovertemplate=f"{ccy}: %{{y:,.0f}}<extra></extra>"))
        apply_dark(fig3,barmode="relative",height=320,
                   title=dict(text=f"{drill} by Currency",font=dict(size=11,color=TEXT2)))
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        ct = ccy_df.groupby("Currency")["Value"].sum().reset_index()
        ct = ct[ct["Value"].abs()>0]
        fig4 = go.Figure(go.Pie(
            labels=ct["Currency"],values=ct["Value"].abs(),hole=0.65,
            marker=dict(colors=[CCY_COLORS.get(c,"#606070") for c in ct["Currency"]],
                        line=dict(color=BG1,width=2)),
            textfont=dict(family="Space Mono",color=TEXT1,size=9),
            hovertemplate="%{label}: %{value:,.0f}<extra></extra>",
        ))
        apply_dark(fig4,height=320,showlegend=True,
                   title=dict(text="Currency Mix (abs) · Period",font=dict(size=11,color=TEXT2)))
        st.plotly_chart(fig4, use_container_width=True)

    sh("Heatmap · Type × Currency")
    heat = (ccy_df.groupby(["PnL Type","Currency"])["Value"].sum().reset_index()
            .pivot(index="PnL Type",columns="Currency",values="Value").fillna(0))
    fig5 = go.Figure(go.Heatmap(
        z=heat.values,x=heat.columns.tolist(),y=heat.index.tolist(),
        colorscale=HEATMAP_SCALE,zmid=0,
        text=[[f"{v:,.0f}" for v in row] for row in heat.values],
        texttemplate="%{text}",textfont=dict(family="Space Mono",size=9,color=TEXT0),
        hovertemplate="Type: %{y}<br>CCY: %{x}<br>PnL: %{z:,.0f}<extra></extra>",
        colorbar=dict(tickfont=dict(family="Space Mono",size=8,color=TEXT2),
                      bgcolor=BG1,bordercolor=BORD),
    ))
    apply_dark(fig5,height=400,title=dict(text="Period PnL — Type × Currency",font=dict(size=11,color=TEXT2)))
    st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3
# ══════════════════════════════════════════════
with tab3:
    sh("Issuer Credit Attribution")
    metric_sel = st.radio("Metric",["CreditPnL","CreditParallel","CreditCurve","Residual"],horizontal=True)
    iss_m = fiss[fiss["Metric"]==metric_sel].copy()

    col_c,col_d = st.columns([3,2])
    with col_c:
        it = (iss_m.groupby(["Date","Issuer"])["Value"].sum().reset_index()
              .pivot(index="Date",columns="Issuer",values="Value").fillna(0).sort_index())
        fig6 = go.Figure()
        for i,iss in enumerate(it.columns):
            fig6.add_trace(go.Bar(x=it.index,y=it[iss],name=iss,
                marker_color=ISSUER_PALETTE[i%len(ISSUER_PALETTE)],
                hovertemplate=f"{iss}: %{{y:,.0f}}<extra></extra>"))
        apply_dark(fig6,barmode="relative",height=380,
                   title=dict(text=f"{metric_sel} by Issuer — Daily",font=dict(size=11,color=TEXT2)))
        st.plotly_chart(fig6, use_container_width=True)

    with col_d:
        it2 = (iss_m.groupby("Issuer")["Value"].sum().sort_values(ascending=True).reset_index())
        fig7 = go.Figure(go.Bar(
            x=it2["Value"],y=it2["Issuer"],orientation="h",
            marker_color=[RED if v<0 else GREEN for v in it2["Value"]],
            text=[f"{v:,.0f}" for v in it2["Value"]],
            textposition="outside",textfont=dict(family="Space Mono",size=8,color=TEXT2),
            hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
        ))
        apply_dark(fig7,height=380,title=dict(text=f"Period Total · {metric_sel}",font=dict(size=11,color=TEXT2)))
        st.plotly_chart(fig7, use_container_width=True)

    sh("All Metrics · Issuer Heatmap")
    ah = (fiss.groupby(["Issuer","Metric"])["Value"].sum().reset_index()
          .pivot(index="Issuer",columns="Metric",values="Value").fillna(0))
    fig8 = go.Figure(go.Heatmap(
        z=ah.values,x=ah.columns.tolist(),y=ah.index.tolist(),
        colorscale=HEATMAP_SCALE,zmid=0,
        text=[[f"{v:,.0f}" for v in row] for row in ah.values],
        texttemplate="%{text}",textfont=dict(family="Space Mono",size=9,color=TEXT0),
        hovertemplate="Issuer: %{y}<br>Metric: %{x}<br>Value: %{z:,.0f}<extra></extra>",
        colorbar=dict(tickfont=dict(family="Space Mono",size=8,color=TEXT2),bgcolor=BG1,bordercolor=BORD),
    ))
    apply_dark(fig8,height=480,title=dict(text="Issuer × Metric Heatmap — Period",font=dict(size=11,color=TEXT2)))
    st.plotly_chart(fig8, use_container_width=True)

    sh(f"Cumulative {metric_sel} by Issuer")
    fig9 = go.Figure()
    for i,iss in enumerate(it.columns):
        cum = it[iss].cumsum()
        fig9.add_trace(go.Scatter(x=cum.index,y=cum,name=iss,mode="lines",
            line=dict(color=ISSUER_PALETTE[i%len(ISSUER_PALETTE)],width=1.4),
            hovertemplate=f"{iss}: %{{y:,.0f}}<extra></extra>"))
    fig9.add_hline(y=0, line_color=BORD2, line_width=1)
    apply_dark(fig9,height=340,title=dict(text=f"Cumulative {metric_sel}",font=dict(size=11,color=TEXT2)))
    st.plotly_chart(fig9, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4
# ══════════════════════════════════════════════
with tab4:
    if frisk.empty:
        st.info("No risk data available.")
    else:
        rsel = st.selectbox("Risk Type", TENOR_CCY_RISK+ISSUER_RISK+["FXBalance"], key="rsel")
        latest_d  = frisk["Date"].max()
        is_tc     = rsel in TENOR_CCY_RISK
        is_iss    = rsel in ISSUER_RISK
        rdata     = frisk[frisk["Risk Type"]==rsel]

        if is_tc:
            sh(f"Tenor × CCY Matrix · {rsel} · {latest_d.strftime('%d %b %Y')}")
            lat  = rdata[rdata["Date"]==latest_d]
            mrows= []
            for t in TENORS:
                row = {"Tenor":t}
                for c in ["Total"]+CCYS:
                    k = f"{t}_{c}" if c!="Total" else t
                    vr = lat[lat["Dimension"]==k]["Value"]
                    row[c] = vr.values[0] if not vr.empty else 0
                mrows.append(row)
            tr = {"Tenor":"Total"}
            for c in ["Total"]+CCYS:
                vr = lat[lat["Dimension"]==c]["Value"]
                tr[c] = vr.values[0] if not vr.empty else 0
            mrows.append(tr)
            mdf = pd.DataFrame(mrows).set_index("Tenor")
            co  = ["Total"]+CCYS
            fh  = go.Figure(go.Heatmap(
                z=mdf[co].values,x=co,y=mdf.index.tolist(),
                colorscale=HEATMAP_SCALE,zmid=0,
                text=[[f"{v:,.0f}" for v in row] for row in mdf[co].values],
                texttemplate="%{text}",textfont=dict(family="Space Mono",size=10,color=TEXT0),
                hovertemplate="Tenor: %{y}<br>CCY: %{x}<br>Value: %{z:,.0f}<extra></extra>",
                colorbar=dict(tickfont=dict(family="Space Mono",size=8,color=TEXT2),bgcolor=BG1,bordercolor=BORD),
            ))
            apply_dark(fh,height=300,title=dict(text=f"{rsel} — Tenor × CCY",font=dict(size=11,color=TEXT2)))
            st.plotly_chart(fh, use_container_width=True)

        if is_iss:
            sh(f"{rsel} by Issuer · {latest_d.strftime('%d %b %Y')}")
            lat = rdata[rdata["Date"]==latest_d]
            il  = (lat[lat["Dimension"].isin(ISSUERS)].groupby("Dimension")["Value"].sum()
                   .sort_values(ascending=True).reset_index())
            fi  = go.Figure(go.Bar(
                x=il["Value"],y=il["Dimension"],orientation="h",
                marker_color=[RED if v<0 else GREEN for v in il["Value"]],
                text=[f"{v:,.0f}" for v in il["Value"]],
                textposition="outside",textfont=dict(family="Space Mono",size=8,color=TEXT2),
                hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
            ))
            apply_dark(fi,height=400,title=dict(text=f"{rsel} by Issuer",font=dict(size=11,color=TEXT2)))
            st.plotly_chart(fi, use_container_width=True)

        sh(f"{rsel} Over Time")
        if is_tc:   dim_opts,defs = ["Total"]+CCYS+TENORS, ["Total"]+CCYS
        elif is_iss: dim_opts,defs = ["Total"]+ISSUERS, ["Total"]
        else:        dim_opts,defs = ["Total"]+CCYS, ["Total"]+CCYS

        dims = st.multiselect("Dimensions", dim_opts, default=defs, key="rdims")
        rts  = (rdata[rdata["Dimension"].isin(dims)]
                .groupby(["Date","Dimension"])["Value"].sum().reset_index()
                .pivot(index="Date",columns="Dimension",values="Value").fillna(0).sort_index())
        fts  = go.Figure()
        for i,d in enumerate(dims):
            if d not in rts.columns: continue
            fts.add_trace(go.Scatter(x=rts.index,y=rts[d],name=d,mode="lines",
                line=dict(color=CCY_COLORS.get(d,ISSUER_PALETTE[i%len(ISSUER_PALETTE)]),width=1.6),
                hovertemplate=f"{d}: %{{y:,.0f}}<extra></extra>"))
        fts.add_hline(y=0,line_color=BORD2,line_width=1)
        apply_dark(fts,height=340,title=dict(text=f"{rsel} — Daily Positions",font=dict(size=11,color=TEXT2)))
        st.plotly_chart(fts, use_container_width=True)

        sh("All Risk Types · Latest Day")
        atl = frisk[(frisk["Date"]==latest_d)&(frisk["Dimension"]=="Total")]
        att = atl.groupby("Risk Type")["Value"].sum().sort_values(ascending=True).reset_index()
        fa  = go.Figure(go.Bar(
            x=att["Value"],y=att["Risk Type"],orientation="h",
            marker_color=[RISK_COLORS.get(r,"#606070") for r in att["Risk Type"]],
            text=[f"{v:,.0f}" for v in att["Value"]],
            textposition="outside",textfont=dict(family="Space Mono",size=8,color=TEXT2),
            hovertemplate="%{y}: %{x:,.0f}<extra></extra>",
        ))
        apply_dark(fa,height=300,title=dict(text=f"Total Risk by Type — {latest_d.strftime('%d %b %Y')}",
                   font=dict(size=11,color=TEXT2)))
        st.plotly_chart(fa, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5
# ══════════════════════════════════════════════
with tab5:
    if fperiod.empty:
        st.info("No MTD/YTD/LTD data.")
    else:
        all_insts = sorted(fperiod["Instrument"].unique())
        lpd       = fperiod["Date"].max()

        sh(f"Latest Snapshot · {lpd.strftime('%d %b %Y')}")
        snap = (fperiod[fperiod["Date"]==lpd]
                .groupby(["Period","Instrument"])["Value"].sum().reset_index()
                .pivot(index="Instrument",columns="Period",values="Value").fillna(0))
        cop  = [p for p in ["MTD","YTD","LTD"] if p in snap.columns]
        snap = snap[cop]
        if "Total" in snap.index:
            snap = pd.concat([snap.loc[["Total"]],snap.drop("Total")])

        def _pc(v,cv):
            mx=max(abs(cv.max()),abs(cv.min()),1)
            return pos_c(v,mx) if v>0 else (neg_c(v,mx) if v<0 else "rgba(20,20,31,1)")

        cc = [["rgba(20,20,31,1)"]*len(snap)]
        for col in cop: cc.append([_pc(v,snap[col]) for v in snap[col]])

        fs = go.Figure(go.Table(
            header=dict(values=["<b>INSTRUMENT</b>"]+[f"<b>{c}</b>" for c in cop],
                fill_color=TBL_HDR_BG,font=dict(family="Space Mono",color=TEXT2,size=9),
                align=["left"]+["right"]*len(cop),line_color=BORD,height=26),
            cells=dict(
                values=[snap.index.tolist()]+[[f"{v:,.0f}" for v in snap[c]] for c in cop],
                fill_color=cc,font=dict(family="Space Mono",color=TEXT1,size=9),
                align=["left"]+["right"]*len(cop),line_color=BORD,height=22),
        ))
        fs.update_layout(**TABLE_LAYOUT,height=72+len(snap)*24)
        st.plotly_chart(fs, use_container_width=True)

        sh("Instrument Breakdown · Latest")
        sr = snap.reset_index()
        fb = go.Figure()
        for p in cop:
            fb.add_trace(go.Bar(x=sr["Instrument"],y=sr[p],name=p,
                marker_color=PERIOD_COLORS.get(p,"#606070"),
                hovertemplate=f"{p}: %{{y:,.0f}}<extra></extra>"))
        apply_dark(fb,barmode="group",height=340,
                   title=dict(text="MTD / YTD / LTD by Instrument",font=dict(size=11,color=TEXT2)))
        st.plotly_chart(fb, use_container_width=True)

        sh("Period Evolution Over Time")
        c1p,c2p = st.columns(2)
        with c1p: pts = st.selectbox("Period",cop,key="pts")
        with c2p: its = st.multiselect("Instruments",all_insts,default=all_insts[:min(5,len(all_insts))],key="its")
        td = (fperiod[(fperiod["Period"]==pts)&(fperiod["Instrument"].isin(its))]
              .groupby(["Date","Instrument"])["Value"].sum().reset_index()
              .pivot(index="Date",columns="Instrument",values="Value").fillna(0).sort_index())
        fe = go.Figure()
        for i,inst in enumerate(its):
            if inst not in td.columns: continue
            fe.add_trace(go.Scatter(x=td.index,y=td[inst],name=inst,mode="lines",
                line=dict(color=ISSUER_PALETTE[i%len(ISSUER_PALETTE)],
                          width=2.2 if inst=="Total" else 1.4),
                hovertemplate=f"{inst}: %{{y:,.0f}}<extra></extra>"))
        fe.add_hline(y=0,line_color=BORD2,line_width=1)
        apply_dark(fe,height=340,title=dict(text=f"{pts} — Daily Evolution",font=dict(size=11,color=TEXT2)))
        st.plotly_chart(fe, use_container_width=True)

        sh("All Periods · Single Instrument")
        si = st.selectbox("Instrument",all_insts,key="si")
        sd = (fperiod[fperiod["Instrument"]==si]
              .groupby(["Date","Period"])["Value"].sum().reset_index()
              .pivot(index="Date",columns="Period",values="Value").fillna(0).sort_index())
        fg = go.Figure()
        for p in cop:
            if p not in sd.columns: continue
            fg.add_trace(go.Scatter(x=sd.index,y=sd[p],name=p,mode="lines",
                line=dict(color=PERIOD_COLORS.get(p,"#606070"),width=1.6),
                hovertemplate=f"{p}: %{{y:,.0f}}<extra></extra>"))
        fg.add_hline(y=0,line_color=BORD2,line_width=1)
        apply_dark(fg,height=300,title=dict(text=f"MTD / YTD / LTD — {si}",font=dict(size=11,color=TEXT2)))
        st.plotly_chart(fg, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 6
# ══════════════════════════════════════════════
with tab6:
    sel = st.radio("Table",["PnL by CCY","Issuer PnL","Risk","MTD YTD LTD"],horizontal=True)
    maps = {"PnL by CCY":(fpnl,"pnl_ccy.csv"),
            "Issuer PnL":(fiss,"issuer_pnl.csv"),
            "Risk":(frisk,"risk.csv"),
            "MTD YTD LTD":(fperiod,"mtd_ytd_ltd.csv")}
    df_raw,fn = maps[sel]
    d = df_raw.copy()
    d["Date"] = d["Date"].dt.strftime("%d %b %Y")
    d["Value"] = d["Value"].round(2)
    st.dataframe(d, use_container_width=True, height=520)
    st.download_button("⬇  Export CSV", d.to_csv(index=False), file_name=fn, mime="text/csv")
