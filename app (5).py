"""
================================================================================
MCI1044 FINAL ASSESSMENT - SDG 11 DASHBOARD (Streamlit)
Monitoring Malaysia's Progress Toward Sustainable Cities, 2018-2023
Student: Katiravan Krishnan (KCA25003)
Run locally:  streamlit run app.py
================================================================================
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

# ----------------------------------------------------------------------------
st.set_page_config(page_title="Malaysia SDG 11 Dashboard",
                   page_icon="🏙️", layout="wide")

# --- SDG 11 theme ---
AMBER, TEAL, CORAL, BLUE, INK, SLATE = "#FD9D24", "#2A9D8F", "#E76F51", "#264653", "#1A2B3C", "#5A6B7B"
REGION_COLORS = {"Central": AMBER, "South": TEAL, "North": BLUE,
                 "East Coast": CORAL, "East Malaysia": "#8E7DBE"}
LAYOUT = dict(font=dict(family="Arial", size=13, color=INK),
              plot_bgcolor="white", paper_bgcolor="white",
              margin=dict(l=50, r=30, t=50, b=40))

st.markdown(f"""
<style>
  .main {{ background:#FBFAF7; }}
  h1,h2,h3 {{ color:{INK}; }}
  .stMetric {{ background:white; border:1px solid #Eee; border-radius:10px; padding:10px; }}
</style>""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load():
    state = pd.read_csv(os.path.join(HERE, "state_profile.csv"))
    national = pd.read_csv(os.path.join(HERE, "national_trend.csv"))
    CENT = {"Johor":(1.93,103.55),"Kedah":(6.12,100.37),"Kelantan":(5.38,102.02),
            "Melaka":(2.19,102.25),"Negeri Sembilan":(2.73,101.94),"Pahang":(3.81,103.33),
            "Perak":(4.59,101.09),"Perlis":(6.44,100.20),"Pulau Pinang":(5.41,100.33),
            "Sabah":(5.98,116.08),"Sarawak":(1.55,110.36),"Selangor":(3.07,101.52),
            "Terengganu":(5.31,103.13),"W.P. Kuala Lumpur":(3.14,101.69),
            "W.P. Labuan":(5.28,115.23),"W.P. Putrajaya":(2.93,101.70)}
    state["lat"]=state.State.map(lambda s:CENT[s][0]); state["lon"]=state.State.map(lambda s:CENT[s][1])
    return state, national

state, national = load()

# ============================ HEADER ========================================
st.title("🏙️ Malaysia SDG 11 — Sustainable Cities & Communities")
st.caption("Progress & Implementation, 2018–2023  |  Sources: DOSM, JKM, JPS (data.gov.my / open.dosm.gov.my)")

c1,c2,c3,c4 = st.columns(4)
c1.metric("National population 2023", f"{state.Pop_2023.sum()/1e6:.2f} M",
          f"{(state.Pop_2023.sum()-state.Pop_2018.sum())/1e6:+.2f} M vs 2018")
c2.metric("Fastest-growing state", "Putrajaya", "+22.2%")
c3.metric("2021 flood evacuees", f"{state.Flood_Evacuees_2021.sum():,}")
c4.metric("PM2.5 drop in 2020", "−40%", "COVID movement control")

st.divider()

# ============================ SIDEBAR FILTERS ===============================
st.sidebar.header("🔎 Filters")
regions = st.sidebar.multiselect("Region", sorted(state.Region.unique()),
                                 default=sorted(state.Region.unique()))
metric = st.sidebar.selectbox("Map bubble size",
                              ["Flood_Evacuees_2021","Flood_Hotspots","Pop_2023"])
fstate = state[state.Region.isin(regions)] if regions else state

# ============================ TABS ==========================================
tab1, tab2, tab3, tab4 = st.tabs(
    ["🗺️ Spatial Map", "🌫️ Air Quality Trend", "🌊 Flood Burden", "📈 Growth vs Risk"])

with tab1:
    st.subheader("Viz 1 — SDG 11 Spatial Snapshot")
    fig = px.scatter_geo(fstate, lat="lat", lon="lon", size=metric,
                         color="Pop_Growth_Pct", color_continuous_scale="RdYlGn",
                         size_max=42, hover_name="State",
                         hover_data={"Pop_Growth_Pct":":.1f","Flood_Evacuees_2021":":,",
                                     "Flood_Hotspots":True,"lat":False,"lon":False})
    fig.update_geos(scope="asia", center=dict(lat=4.2,lon=109), projection_scale=4.4,
                    showcountries=True, landcolor="#F4E9DA", showland=True,
                    oceancolor="#EAF3F5", showocean=True)
    fig.update_layout(**LAYOUT, height=520, coloraxis_colorbar=dict(title="Pop growth %"))
    st.plotly_chart(fig, use_container_width=True)
    st.info("Population growth concentrates in the central Klang Valley (green), while the "
            "largest flood-evacuee bubbles sit on the east coast (Pahang) and East Malaysia.")

with tab2:
    st.subheader("Viz 2 — National Particulate Matter Trend")
    ap = national.dropna(subset=["PM_2.5"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ap.year,y=ap["PM_2.5"],name="PM2.5",mode="lines+markers",
                             line=dict(color=CORAL,width=3.5)))
    fig.add_trace(go.Scatter(x=ap.year,y=ap["PM_10"],name="PM10",mode="lines+markers",
                             line=dict(color=AMBER,width=3.5)))
    fig.add_hline(y=5,line_dash="dot",line_color=SLATE,
                  annotation_text="WHO PM2.5 guideline (5 µg/m³)")
    fig.update_layout(**LAYOUT,height=480,xaxis_title="Year",yaxis_title="Annual mean (µg/m³)")
    st.plotly_chart(fig, use_container_width=True)
    st.info("PM2.5 fell ~40% in 2020 during COVID-19 movement controls and stayed low — "
            "yet all years remain far above the WHO 5 µg/m³ guideline.")

with tab3:
    st.subheader("Viz 3 — Flood Burden by State")
    f = fstate.sort_values("Flood_Evacuees_2021")
    fig = make_subplots(rows=1,cols=2,shared_yaxes=True,
                        subplot_titles=("Flood evacuees (2021)","Active hotspots"))
    fig.add_trace(go.Bar(y=f.State,x=f.Flood_Evacuees_2021,orientation="h",
                         marker_color=CORAL),row=1,col=1)
    fig.add_trace(go.Bar(y=f.State,x=f.Flood_Hotspots,orientation="h",
                         marker_color=BLUE),row=1,col=2)
    fig.update_layout(**LAYOUT,height=520,showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    st.info("Pahang alone accounts for ~41% of 2021 evacuees; Sarawak leads in chronic "
            "flash-flood hotspots — two distinct flood profiles requiring different responses.")

with tab4:
    st.subheader("Viz 4 — Urban Growth vs Flood Risk")
    fig = px.scatter(fstate, x="Flood_Hotspots", y="Pop_Growth_Pct", size="Pop_2023",
                     color="Region", color_discrete_map=REGION_COLORS, size_max=55,
                     hover_name="State", text="State")
    fig.update_traces(textposition="top center", textfont=dict(size=9,color=SLATE))
    fig.add_hline(y=0,line_dash="dot",line_color=SLATE)
    fig.update_layout(**LAYOUT,height=520,xaxis_title="Active flash-flood hotspots",
                      yaxis_title="Population growth 2018–2023 (%)")
    st.plotly_chart(fig, use_container_width=True)
    st.info("Fast-growing states cluster at low hotspot counts (r = −0.56): urban growth "
            "favours safer central areas, while flood-prone East Malaysia states decline.")

st.divider()
with st.expander("📋 View underlying state data"):
    st.dataframe(fstate, use_container_width=True)
