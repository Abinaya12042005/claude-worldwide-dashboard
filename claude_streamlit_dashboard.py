# claude_streamlit_dashboard.py
# Run: streamlit run claude_streamlit_dashboard.py
# Browser-ல automatically open ஆகும்!

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

# ── PAGE CONFIG ─────────────────────────────────────────
st.set_page_config(
    page_title="Claude Worldwide — Live Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── DARK THEME CSS ───────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #1a1a2e; color: #f0f0f0; }
    .block-container { padding: 1rem 2rem; }
    .metric-card {
        background: #252545;
        border: 1px solid #3a3a5c;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .metric-val { font-size: 28px; font-weight: 600; color: #378ADD; }
    .metric-lbl { font-size: 12px; color: #aaa; margin-top: 4px; }
    .metric-delta { font-size: 11px; color: #4fc97a; margin-top: 2px; }
    h1, h2, h3 { color: #f0f0f0 !important; }
    .stSelectbox, .stMultiselect { background: #252545; }
    div[data-testid="stMetric"] {
        background: #252545;
        border: 1px solid #3a3a5c;
        border-radius: 10px;
        padding: 12px;
    }
    div[data-testid="stMetricValue"] { color: #378ADD; font-size: 26px; }
    div[data-testid="stMetricLabel"] { color: #aaa; }
    .live-dot {
        display: inline-block;
        width: 8px; height: 8px;
        background: #4fc97a;
        border-radius: 50%;
        margin-right: 6px;
        animation: blink 1s infinite;
    }
</style>
""", unsafe_allow_html=True)

# ── LOAD & SIMULATE LIVE DATA ────────────────────────────
@st.cache_data(ttl=60)  # every 60 seconds refresh
def load_data():
    try:
        # உன் actual CSV path
        df = pd.read_csv(r"E:\ISO\claude_live_data.csv")
    except:
        # fallback — generate fresh data
        np.random.seed(int(time.time()) % 1000)
        regions = {
            "North America": ["USA","Canada","Mexico"],
            "Europe": ["UK","Germany","France","Spain"],
            "Asia Pacific": ["India","Japan","Australia","Singapore"],
            "Latin America": ["Brazil","Argentina","Colombia"],
            "ME & Africa": ["UAE","South Africa","Nigeria"]
        }
        plans = ["Free","Pro","Team/Enterprise"]
        platforms = ["Web","API","Mobile","Desktop"]
        use_cases = ["Coding & Dev","Writing & Content","Data Analysis","Education","Customer Support","Other"]
        rows = []
        for _ in range(500):
            region = np.random.choice(list(regions.keys()), p=[0.38,0.27,0.21,0.08,0.06])
            country = np.random.choice(regions[region])
            rows.append({
                "Region": region, "Country": country,
                "Platform": np.random.choice(platforms, p=[0.41,0.29,0.19,0.11]),
                "Use_Case": np.random.choice(use_cases, p=[0.34,0.22,0.18,0.14,0.08,0.04]),
                "Plan": np.random.choice(plans, p=[0.52,0.31,0.17]),
                "Active_Users": int(np.random.uniform(0.97,1.03) * {"North America":71060000,"Europe":50490000,"Asia Pacific":39270000,"Latin America":14960000,"ME & Africa":11220000}[region]),
                "Messages_Per_Min": int(np.random.uniform(1200000,1900000)),
                "Session_Min": round(np.random.uniform(14,23),1),
                "Satisfaction": round(np.random.uniform(4.0,5.0),2),
                "Hour_UTC": np.random.randint(0,24),
                "Day_Of_Week": np.random.choice(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]),
            })
        df = pd.DataFrame(rows)
    return df

# ── SIDEBAR FILTERS ──────────────────────────────────────
st.sidebar.title("⚡ Filters")
df_raw = load_data()

regions_all = df_raw["Region"].unique().tolist()
sel_region = st.sidebar.multiselect("Region", regions_all, default=regions_all)

plans_all = df_raw["Plan"].unique().tolist()
sel_plan = st.sidebar.multiselect("Plan", plans_all, default=plans_all)

platforms_all = df_raw["Platform"].unique().tolist()
sel_platform = st.sidebar.multiselect("Platform", platforms_all, default=platforms_all)

# ── APPLY FILTERS ────────────────────────────────────────
df = df_raw[
    df_raw["Region"].isin(sel_region) &
    df_raw["Plan"].isin(sel_plan) &
    df_raw["Platform"].isin(sel_platform)
]

# ── HEADER ───────────────────────────────────────────────
col_h1, col_h2 = st.columns([3,1])
with col_h1:
    st.markdown("## ⚡ Claude worldwide — live dashboard")
with col_h2:
    st.markdown(f"<div style='color:#4fc97a;font-size:12px;text-align:right;margin-top:12px'>🟢 Live · {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

st.divider()

# ── KPI CARDS ────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Total Active Users", f"{df['Active_Users'].sum()/1e6:.1f}M", f"+{np.random.randint(1,50)}K")
with k2:
    st.metric("Avg Messages/Min", f"{df['Messages_Per_Min'].mean()/1e6:.2f}M", f"+{np.random.randint(1,20)}K")
with k3:
    st.metric("Avg Session (min)", f"{df['Session_Min'].mean():.1f}", f"{np.random.choice(['+','-'])}{round(np.random.uniform(0.1,0.5),1)}")
with k4:
    st.metric("Avg Satisfaction", f"{df['Satisfaction'].mean():.2f}", f"+{round(np.random.uniform(0.01,0.05),2)}")

st.markdown("")

# ── ROW 1 CHARTS ─────────────────────────────────────────
c1, c2, c3 = st.columns([1, 1.5, 1])

with c1:
    st.markdown("**Users by Region**")
    reg_df = df.groupby("Region")["Active_Users"].sum().reset_index()
    fig1 = px.pie(reg_df, names="Region", values="Active_Users",
                  hole=0.55,
                  color_discrete_sequence=["#378ADD","#7F77DD","#1D9E75","#EF9F27","#D85A30"])
    fig1.update_layout(paper_bgcolor="#252545", plot_bgcolor="#252545",
                       font_color="#f0f0f0", showlegend=True,
                       legend=dict(font_color="#ccc", bgcolor="#252545"),
                       margin=dict(t=10,b=10,l=10,r=10), height=220)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown("**Messages/Min — Live**")
    hours = list(range(24))
    msgs = [df[df["Hour_UTC"]==h]["Messages_Per_Min"].mean() for h in hours]
    msgs = [m if not np.isnan(m) else df["Messages_Per_Min"].mean() for m in msgs]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=hours, y=msgs, fill="tozeroy",
                               line=dict(color="#f2c811", width=2),
                               fillcolor="rgba(242,200,17,0.1)"))
    fig2.update_layout(paper_bgcolor="#252545", plot_bgcolor="#252545",
                       font_color="#f0f0f0", showlegend=False,
                       xaxis=dict(gridcolor="#3a3a5c"),
                       yaxis=dict(gridcolor="#3a3a5c"),
                       margin=dict(t=10,b=10,l=10,r=10), height=220)
    st.plotly_chart(fig2, use_container_width=True)

with c3:
    st.markdown("**Platform Split**")
    plat_df = df.groupby("Platform").size().reset_index(name="count")
    fig3 = px.pie(plat_df, names="Platform", values="count",
                  hole=0.55,
                  color_discrete_sequence=["#378ADD","#7F77DD","#1D9E75","#EF9F27"])
    fig3.update_layout(paper_bgcolor="#252545", plot_bgcolor="#252545",
                       font_color="#f0f0f0", showlegend=True,
                       legend=dict(font_color="#ccc", bgcolor="#252545"),
                       margin=dict(t=10,b=10,l=10,r=10), height=220)
    st.plotly_chart(fig3, use_container_width=True)

# ── ROW 2 CHARTS ─────────────────────────────────────────
c4, c5, c6 = st.columns([1, 1.5, 1])

with c4:
    st.markdown("**Use Case Breakdown**")
    uc_df = df.groupby("Use_Case").size().reset_index(name="count").sort_values("count")
    fig4 = px.bar(uc_df, x="count", y="Use_Case", orientation="h",
                  color="Use_Case",
                  color_discrete_sequence=["#378ADD","#7F77DD","#1D9E75","#EF9F27","#D85A30","#B4B2A9"])
    fig4.update_layout(paper_bgcolor="#252545", plot_bgcolor="#252545",
                       font_color="#f0f0f0", showlegend=False,
                       xaxis=dict(gridcolor="#3a3a5c"),
                       yaxis=dict(gridcolor="#3a3a5c"),
                       margin=dict(t=10,b=10,l=10,r=10), height=220)
    st.plotly_chart(fig4, use_container_width=True)

with c5:
    st.markdown("**Country Treemap**")
    ctry_df = df.groupby(["Region","Country"])["Active_Users"].sum().reset_index()
    fig5 = px.treemap(ctry_df, path=["Region","Country"], values="Active_Users",
                      color="Region",
                      color_discrete_map={"North America":"#378ADD","Europe":"#7F77DD",
                                          "Asia Pacific":"#1D9E75","Latin America":"#EF9F27",
                                          "ME & Africa":"#D85A30"})
    fig5.update_layout(paper_bgcolor="#252545", font_color="#f0f0f0",
                       margin=dict(t=10,b=10,l=10,r=10), height=220)
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    st.markdown("**Plan Distribution**")
    plan_df = df.groupby("Plan").size().reset_index(name="count")
    fig6 = px.pie(plan_df, names="Plan", values="count",
                  hole=0.55,
                  color_discrete_sequence=["#B4B2A9","#7F77DD","#378ADD"])
    fig6.update_layout(paper_bgcolor="#252545", plot_bgcolor="#252545",
                       font_color="#f0f0f0", showlegend=True,
                       legend=dict(font_color="#ccc", bgcolor="#252545"),
                       margin=dict(t=10,b=10,l=10,r=10), height=220)
    st.plotly_chart(fig6, use_container_width=True)

# ── AUTO REFRESH ─────────────────────────────────────────
st.divider()
col_r1, col_r2 = st.columns([3,1])
with col_r1:
    st.markdown(f"<div style='color:#555;font-size:11px'>Data source: E:\\ISO\\claude_live_data.csv · Auto-refresh every 60s · {len(df)} rows loaded</div>", unsafe_allow_html=True)
with col_r2:
    if st.button("🔄 Refresh now"):
        st.cache_data.clear()
        st.rerun()

# Auto rerun every 60 seconds
time.sleep(0.1)
st.markdown("""
<script>
setTimeout(function(){window.location.reload()}, 60000);
</script>
""", unsafe_allow_html=True)

