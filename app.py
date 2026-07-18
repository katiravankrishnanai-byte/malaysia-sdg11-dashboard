
"""
===============================================================
MCI1044 FINAL ASSESSMENT - SDG 11 DASHBOARD (Streamlit)
==============================================================
"""

import os
from typing import Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Malaysia SDG 11 Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# THEME
# =============================================================================
AMBER = "#FD9D24"       # SDG 11 official colour
AMBER_DARK = "#D97800"
CREAM = "#FFF7ED"
CARD = "#FFFFFF"
TEAL = "#2A9D8F"
CORAL = "#E76F51"
BLUE = "#264653"
INK = "#1A2B3C"
SLATE = "#5A6B7B"
LIGHT_BORDER = "#E9EEF3"
PURPLE = "#8E7DBE"

REGION_COLORS = {
    "Central": AMBER,
    "South": TEAL,
    "North": BLUE,
    "East Coast": CORAL,
    "East Malaysia": PURPLE,
}

PLOTLY_LAYOUT = dict(
    font=dict(family="Arial, sans-serif", size=13, color=INK),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=55, r=35, t=60, b=45),
)

st.markdown(
    f"""
<style>
    /* Main page background: warm SDG 11 executive theme */
    .stApp {{
        background: linear-gradient(180deg, #FFF8EE 0%, #FFFDF8 48%, #FFFFFF 100%);
    }}

    /* Sidebar: darker executive control panel */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #DDE7EF 0%, #C9D8E6 100%);
        border-right: 1px solid #B8C7D6;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {{
        color: {INK} !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background-color: #FFFFFF;
        border-radius: 10px;
    }}
    section[data-testid="stSidebar"] .stCheckbox {{
        margin-top: 8px;
    }}

    /* Executive title banner */
    .main-banner {{
        background: linear-gradient(135deg, #FD9D24 0%, #F1873B 45%, #E76F51 100%);
        border-radius: 22px;
        padding: 30px 34px;
        color: #FFFFFF;
        box-shadow: 0 12px 30px rgba(231, 111, 81, 0.24);
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.35);
    }}
    .main-title {{
        color: #FFFFFF;
        font-size: 2.25rem;
        font-weight: 850;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }}
    .main-subtitle {{
        color: #FFFFFF;
        font-size: 1.05rem;
        margin-top: 4px;
        max-width: 1080px;
        line-height: 1.55;
    }}
    .small-note {{
        color: rgba(255,255,255,0.92);
        font-size: 0.90rem;
        margin-top: 12px;
    }}

    /* KPI cards */
    div[data-testid="stMetric"] {{
        background: #FFFFFF;
        border: 1px solid #F4C27A;
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 7px 18px rgba(26, 43, 60, 0.08);
    }}
    div[data-testid="stMetric"] label {{
        color: {SLATE};
        font-size: 0.92rem;
        font-weight: 650;
    }}
    div[data-testid="stMetricValue"] {{
        color: {INK};
        font-weight: 850;
    }}
    div[data-testid="stMetricDelta"] {{
        font-weight: 650;
    }}

    /* Insight and section cards */
    .insight-box {{
        background: #FFFFFF;
        border-left: 7px solid #FD9D24;
        border-radius: 15px;
        padding: 15px 18px;
        margin-top: 14px;
        box-shadow: 0 5px 16px rgba(26,43,60,0.07);
        color: {INK};
        line-height: 1.55;
    }}
    .section-card {{
        background: #FFFFFF;
        border: 1px solid #F4C27A;
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 5px 16px rgba(26,43,60,0.07);
        margin-bottom: 16px;
    }}

    /* Headings and tabs */
    h1, h2, h3 {{ color: {INK}; }}
    button[data-baseweb="tab"] {{
        font-weight: 650;
        color: #3C4654;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: #E76F51;
        border-bottom: 3px solid #E76F51;
    }}

    /* Data table readability */
    .dataframe {{ font-size: 0.88rem; }}
</style>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# LOAD DATA
# =============================================================================
HERE = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    state_path = os.path.join(HERE, "state_profile.csv")
    national_path = os.path.join(HERE, "national_trend.csv")
    flood_path = os.path.join(HERE, "flood_impact_comparison_2021_2022.csv")
    legacy_flood_path = os.path.join(HERE, "flood_impact_trend_2021_2023.csv")

    if not os.path.exists(state_path):
        st.error("Missing file: state_profile.csv. Please place it in the same folder as app.py.")
        st.stop()
    if not os.path.exists(national_path):
        st.error("Missing file: national_trend.csv. Please place it in the same folder as app.py.")
        st.stop()

    state = pd.read_csv(state_path)
    national = pd.read_csv(national_path)

    if os.path.exists(flood_path):
        flood_trend = pd.read_csv(flood_path)
    elif os.path.exists(legacy_flood_path):
        # Backward compatibility for repositories using the earlier filename.
        flood_trend = pd.read_csv(legacy_flood_path)
    else:
        # Safe fallback so the dashboard still runs during review.
        flood_trend = pd.DataFrame({
            "Period": ["2021", "2022"],
            "Display_Year": [2021, 2022],
            "Flood_Evacuees": [int(state["Flood_Evacuees_2021"].sum()), 251799],
            "Source": ["JKM state-level flood evacuee dataset", "NADMA official reporting"],
            "Data_Level": ["Calendar-year state aggregation", "National annual figure"],
            "Notes": [
                "Sum of the retained 2021 state-level records in the cleaned dashboard data.",
                "NADMA reported 251,799 victims evacuated in 2022. The figure is contextual and is not directly comparable with the JKM state-level sum because source coverage and aggregation differ.",
            ],
        })

    centroids = {
        "Johor": (1.93, 103.55),
        "Kedah": (6.12, 100.37),
        "Kelantan": (5.38, 102.02),
        "Melaka": (2.19, 102.25),
        "Negeri Sembilan": (2.73, 101.94),
        "Pahang": (3.81, 103.33),
        "Perak": (4.59, 101.09),
        "Perlis": (6.44, 100.20),
        "Pulau Pinang": (5.41, 100.33),
        "Sabah": (5.98, 116.08),
        "Sarawak": (1.55, 110.36),
        "Selangor": (3.07, 101.52),
        "Terengganu": (5.31, 103.13),
        "W.P. Kuala Lumpur": (3.14, 101.69),
        "W.P. Labuan": (5.28, 115.23),
        "W.P. Putrajaya": (2.93, 101.70),
    }

    state["lat"] = state["State"].map(lambda s: centroids.get(s, (None, None))[0])
    state["lon"] = state["State"].map(lambda s: centroids.get(s, (None, None))[1])
    state = state.dropna(subset=["lat", "lon"])

    return state, national, flood_trend

state, national, flood_trend = load_data()

# =============================================================================
# DERIVED VALUES
# =============================================================================
fastest_row = state.loc[state["Pop_Growth_Pct"].idxmax()]
highest_flood = flood_trend.loc[flood_trend["Flood_Evacuees"].idxmax()]
highest_state_flood = state.loc[state["Flood_Evacuees_2021"].idxmax()]
most_hotspots = state.loc[state["Flood_Hotspots"].idxmax()]

ap = national.dropna(subset=["PM_2.5"]).copy() if "PM_2.5" in national.columns else pd.DataFrame()
if not ap.empty and {2019, 2020}.issubset(set(ap["year"].astype(int))):
    pm2019 = float(ap.loc[ap["year"].astype(int) == 2019, "PM_2.5"].iloc[0])
    pm2020 = float(ap.loc[ap["year"].astype(int) == 2020, "PM_2.5"].iloc[0])
    pm_drop_pct = ((pm2020 - pm2019) / pm2019) * 100
else:
    pm2019, pm2020, pm_drop_pct = None, None, -40.0

corr_growth_hotspot = state["Pop_Growth_Pct"].corr(state["Flood_Hotspots"])

# =============================================================================
# SIDEBAR
# =============================================================================
st.sidebar.markdown("### 🏙️ SDG 11 Interactive Controls")
st.sidebar.caption(
    "Use these controls to explore state-level SDG 11 patterns. "
    "National air-quality trends remain unchanged because they are not state-specific."
)

regions = st.sidebar.multiselect(
    "Region filter",
    options=sorted(state["Region"].dropna().unique()),
    default=sorted(state["Region"].dropna().unique()),
)

selected_state = st.sidebar.selectbox(
    "Selected state / territory",
    options=sorted(state["State"].unique()),
    index=sorted(state["State"].unique()).index(str(fastest_row["State"])) if str(fastest_row["State"]) in sorted(state["State"].unique()) else 0,
)

metric_label_map = {
    "Flood impact: evacuees in 2021": "Flood_Evacuees_2021",
    "Flood risk exposure: active hotspots": "Flood_Hotspots",
    "Population concentration: 2023 population": "Pop_2023",
}
metric_explanation = {
    "Flood impact: evacuees in 2021": (
        "Bubble size shows the number of people displaced by floods in 2021. "
        "Choose this to identify states with the highest actual flood impact."
    ),
    "Flood risk exposure: active hotspots": (
        "Bubble size shows the number of active flash-flood hotspot locations. "
        "Choose this to identify states with higher recurring flood-risk exposure."
    ),
    "Population concentration: 2023 population": (
        "Bubble size shows the 2023 population size. "
        "Choose this to identify states where larger urban populations are concentrated."
    ),
}
metric_label = st.sidebar.selectbox(
    "Executive map bubble size represents",
    list(metric_label_map.keys()),
    index=0,
    help="This changes the bubble size in the Executive State Sustainability Overview map only."
)
metric = metric_label_map[metric_label]
st.sidebar.caption(metric_explanation[metric_label])

show_state_labels = st.sidebar.checkbox(
    "Show state labels in scatter",
    value=True,
    help="This controls only the Urban Population Growth chart."
)
show_trendline = st.sidebar.checkbox(
    "Show linear trendline",
    value=True,
    help=(
        "The dashed line shows the overall relationship between flood-hotspot exposure "
        "and population growth. A downward line suggests that states with more hotspots "
        "generally have lower population growth, but it does not prove causation."
    ),
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filter scope")
st.sidebar.caption(
    "Region filter updates the state-level visuals: Executive State Sustainability Overview, "
    "Flood Impact & Hotspots, and Urban Population Growth. Air Quality Trend is national-level, "
    "so it is not affected by region or state filters."
)
st.sidebar.caption(
    "The map bubble-size selector affects only the Executive State Sustainability Overview map. "
    "The label and trendline options affect only the Urban Population Growth chart."
)

fstate = state[state["Region"].isin(regions)].copy() if regions else state.copy()
selected_row = state[state["State"] == selected_state].iloc[0]

# =============================================================================
# HEADER
# =============================================================================
st.markdown(
    f"""
<div class="main-banner">
    <div class="main-title">Malaysia SDG 11: Sustainable Cities and Communities</div>
    <div class="main-subtitle">
        Interactive dashboard for monitoring Malaysia's state population growth (used as a proxy for urbanisation pressure), air quality, flood impact, and hotspot exposure from 2018 to 2023.
    </div>
    <div class="small-note">
        Sources: DOSM, DOE, JKM, JPS and NADMA | Focus: SDG 11 — inclusive, safe, resilient and sustainable cities.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# KPI CARDS
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "National population 2023",
        f"{state['Pop_2023'].sum()/1e6:.2f} M",
        f"{(state['Pop_2023'].sum()-state['Pop_2018'].sum())/1e6:+.2f} M vs 2018",
    )
    with st.popover("ℹ️ More info"):
        st.write(
            "This shows Malaysia’s total population in 2023 based on the state-level population dataset. "
            "It gives the overall population base for SDG 11 urban-planning analysis."
        )

with k2:
    st.metric(
        "Fastest state population growth",
        str(fastest_row["State"]).replace("W.P. ", ""),
        f"{float(fastest_row['Pop_Growth_Pct']):+.1f}% from 2018–2023",
    )
    with st.popover("ℹ️ More info"):
        st.write(
            "Putrajaya recorded the fastest overall state-level population growth from 2018 to 2023. "
            "The increase may be associated with its planned federal administrative-city role, housing and public facilities, transport connectivity, and green-city planning. "
            "Population growth is used here as a proxy for urbanisation pressure, not as a direct measure of the urban population share."
        )

with k3:
    st.metric(
        "Highest available flood-impact figure",
        f"{int(highest_flood['Flood_Evacuees']):,}",
        str(highest_flood["Period"]),
    )
    with st.popover("ℹ️ More info"):
        st.write(
            "This KPI highlights the largest official evacuation figure included in the compiled flood evidence. "
            "NADMA reported 251,799 victims evacuated in 2022. This national figure is shown separately from the 2021 JKM state-level sum because the two sources use different coverage and aggregation methods."
        )

with k4:
    st.metric(
        "PM2.5 reduction in 2020",
        f"{pm_drop_pct:.0f}%" if pm_drop_pct is not None else "−40%",
        "Lower transport & activity during MCO",
    )
    with st.popover("ℹ️ More info"):
        st.write(
            "PM2.5 fell sharply in 2020 mainly due to reduced transport, industrial activity, construction and urban movement during the COVID-19 Movement Control Order. "
            "However, the value remained above the WHO annual guideline, so long-term air-quality improvement is still needed."
        )

st.markdown(
    """
<div class="insight-box">
<b>Fastest population-growth explanation:</b> Putrajaya recorded the fastest overall state-level population growth from 2018 to 2023 at +22.2%. The increase may be associated with its planned federal administrative-city role, housing and public facilities, transport connectivity, and green-city planning. In this study, overall population growth is treated as a proxy for urbanisation pressure rather than a direct urban-population measure.
</div>
""",
    unsafe_allow_html=True,
)

st.caption(
    "Flood-impact comparison uses a 2021 JKM state-level sum and a NADMA-reported national evacuation figure for 2022. "
    "The figures provide contextual evidence but should not be interpreted as a directly comparable time series because source coverage and aggregation differ."
)

# =============================================================================
# TABS
# =============================================================================
main_tabs = st.tabs([
    "📌 Executive Overview",
    "📊 Indicator Dashboards",
    "📈 Summary Statistics",
    "💡 Five Key Insights",
    "📂 Data & Evidence",
])

# =============================================================================
# TAB 1: EXECUTIVE DASHBOARD
# =============================================================================
with main_tabs[0]:
    st.subheader("Executive Overview")
    st.write(
        "This page summarises the main SDG 11 findings before users explore the detailed charts. "
        "The indicators cover state population growth as a proxy for urbanisation pressure, particulate air pollution, flood evacuees, and flash-flood hotspot exposure."
    )

    c1, c2 = st.columns([1.2, 1])
    with c1:
        # Population growth ranking chart
        growth_rank = state.sort_values("Pop_Growth_Pct", ascending=True)
        fig_rank = px.bar(
            growth_rank,
            x="Pop_Growth_Pct",
            y="State",
            orientation="h",
            color="Pop_Growth_Pct",
            color_continuous_scale="RdYlGn",
            title="State Population Growth Ranking, 2018–2023",
            labels={"Pop_Growth_Pct": "Population growth 2018–2023 (%)", "State": "State / territory"},
        )
        fig_rank.update_layout(**PLOTLY_LAYOUT, height=580, coloraxis_showscale=False)
        fig_rank.add_vline(x=0, line_dash="dot", line_color=SLATE)
        st.plotly_chart(fig_rank, use_container_width=True)
        st.info(
            "This chart ranks all Malaysian states and federal territories by population growth from 2018 to 2023. "
            "It is a fixed ranking based on the selected dataset, but the Plotly chart remains interactive through hover labels, zooming, and export tools. "
            "W.P. Putrajaya recorded the highest overall state-level population growth at +22.2%, while Sabah and Sarawak show apparent declines that should be interpreted carefully because the series includes the 2020 census rebasing effect."
        )
    with c2:
        st.markdown("#### Selected State / Territory Snapshot")
        st.caption(
            "This snapshot updates based on the state or federal territory selected in the sidebar. "
            "It summarises the selected area’s population, population growth, 2021 flood evacuees, "
            "and active flash-flood hotspot exposure."
        )
        snapshot_df = pd.DataFrame([
            {"Indicator": "Selected state / territory", "Value": selected_state},
            {"Indicator": "Population in 2023", "Value": f"{int(selected_row['Pop_2023']):,}"},
            {"Indicator": "Population growth, 2018–2023", "Value": f"{float(selected_row['Pop_Growth_Pct']):+.1f}%"},
            {"Indicator": "Flood evacuees in 2021", "Value": f"{int(selected_row['Flood_Evacuees_2021']):,}"},
            {"Indicator": "Active flash-flood hotspots (structural risk)", "Value": f"{int(selected_row['Flood_Hotspots']):,}"},
        ])
        st.dataframe(snapshot_df, use_container_width=True, hide_index=True)
        st.info(
            f"{selected_state} is currently selected. The values above update automatically when another state or federal territory is chosen from the sidebar."
        )

    st.markdown(
        """
<div class="insight-box">
<b>Dashboard reading guide:</b> Higher state population growth indicates increasing development and service pressure, while high flood-evacuee and hotspot counts indicate disaster-resilience pressure. Population growth is used as a proxy for urbanisation pressure, so SDG 11 planning should interpret it alongside environmental and resilience indicators.
</div>
""",
        unsafe_allow_html=True,
    )

# =============================================================================
# TAB 2: CORE VISUALISATIONS
# =============================================================================
with main_tabs[1]:
    viz_tabs = st.tabs([
        "🗺️ State Sustainability Overview",
        "🌫️ Air Quality Trend",
        "🌊 Flood Impact & Hotspots",
        "📈 Urban Population Growth",
    ])

    # State Sustainability Overview
    with viz_tabs[0]:
        st.subheader("Executive State Sustainability Overview")
        st.markdown(
            "**What this shows:** This executive map summarises Malaysia’s SDG 11 state-level picture by combining population growth with the selected indicator, such as flood evacuees, flood hotspots, or 2023 population. It helps decision-makers quickly see which states have stronger urban growth and which areas carry higher disaster-resilience pressure."
        )
        fig = px.scatter_geo(
            fstate,
            lat="lat",
            lon="lon",
            size=metric,
            color="Pop_Growth_Pct",
            color_continuous_scale="RdYlGn",
            size_max=42,
            hover_name="State",
            custom_data=["Flood_Evacuees_2021", "Flood_Hotspots", "Pop_2023", "Pop_Growth_Pct"],
            labels={
                "Pop_Growth_Pct": "Population growth 2018–2023 (%)",
                "Flood_Evacuees_2021": "Flood evacuees in 2021",
                "Flood_Hotspots": "Active flash-flood hotspots",
                "Pop_2023": "Population in 2023",
                "State": "State / territory",
            },
        )
        fig.update_geos(
            scope="asia",
            center=dict(lat=4.2, lon=109),
            projection_scale=4.4,
            showcountries=True,
            landcolor="#F4E9DA",
            showland=True,
            oceancolor="#EAF3F5",
            showocean=True,
        )
        fig.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Flood evacuees in 2021: %{customdata[0]:,}<br>"
                "Active flash-flood hotspots: %{customdata[1]:,}<br>"
                "Population in 2023: %{customdata[2]:,}<br>"
                "Population growth 2018–2023: %{customdata[3]:.1f}%"
                "<extra></extra>"
            )
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=560, coloraxis_colorbar=dict(title="Population growth 2018–2023 (%)"))
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            "This executive map uses colour to show population growth from 2018 to 2023, while bubble size changes based on the selected indicator. "
            "For lecturer review, the recommended default is flood impact because it highlights where flood displacement was most severe."
        )

    # Air Quality Trend
    with viz_tabs[1]:
        st.subheader("Air Quality Trend in Malaysia")
        st.markdown("**What this shows:** This line chart shows Malaysia’s annual PM2.5 and PM10 trend, including the sharp 2020 PM2.5 reduction linked to reduced movement and activity during the COVID-19 MCO.")
        if ap.empty:
            st.warning("PM2.5 data not found in national_trend.csv.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=ap["year"],
                y=ap["PM_2.5"],
                name="PM2.5",
                mode="lines+markers",
                line=dict(color=CORAL, width=3.5),
                hovertemplate="Year: %{x}<br>PM2.5 annual mean: %{y:.2f} µg/m³<extra></extra>",
            ))
            if "PM_10" in ap.columns:
                fig.add_trace(go.Scatter(
                    x=ap["year"],
                    y=ap["PM_10"],
                    name="PM10",
                    mode="lines+markers",
                    line=dict(color=AMBER, width=3.5),
                    hovertemplate="Year: %{x}<br>PM10 annual mean: %{y:.2f} µg/m³<extra></extra>",
                ))
            fig.add_hline(
                y=5,
                line_dash="dot",
                line_color=SLATE,
                annotation_text="WHO PM2.5 guideline (5 µg/m³)",
                annotation_position="bottom right",
            )
            fig.update_layout(
                **PLOTLY_LAYOUT,
                height=520,
                title="National Particulate Matter Trend, 2018–2022",
                xaxis_title="Year",
                yaxis_title="Annual mean concentration (µg/m³)",
            )
            fig.update_xaxes(dtick=1)
            st.plotly_chart(fig, use_container_width=True)
        st.info(
            "PM2.5 fell sharply in 2020, coinciding with reduced transport, industrial activity, construction, and urban movement during the COVID-19 Movement Control Order, and remained at a lower level through 2022. "
            "Nevertheless, every observed annual value remained above the WHO annual guideline, showing that sustained long-term air-quality action is still needed."
        )

    # Flood Impact & Hotspots
    with viz_tabs[2]:
        st.subheader("Flood Impact and Hotspot Exposure by State")
        st.markdown("**What this shows:** This comparison separates actual flood evacuees in 2021 from recurring flash-flood hotspot exposure. Flood evacuees represent event impact, while hotspots represent longer-term structural flood-risk exposure.")
        f = fstate.sort_values("Flood_Evacuees_2021", ascending=True)
        fig = make_subplots(
            rows=1,
            cols=2,
            shared_yaxes=True,
            subplot_titles=("Flood evacuees in 2021", "Active flash-flood hotspots (structural risk)"),
            horizontal_spacing=0.08,
        )
        fig.add_trace(
            go.Bar(
                y=f["State"],
                x=f["Flood_Evacuees_2021"],
                orientation="h",
                marker_color=CORAL,
                name="Flood evacuees in 2021",
                hovertemplate="<b>%{y}</b><br>Flood evacuees in 2021: %{x:,}<extra></extra>",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Bar(
                y=f["State"],
                x=f["Flood_Hotspots"],
                orientation="h",
                marker_color=BLUE,
                name="Active flash-flood hotspots (structural risk)",
                hovertemplate="<b>%{y}</b><br>Active flash-flood hotspots (structural risk): %{x:,}<extra></extra>",
            ),
            row=1,
            col=2,
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=560, showlegend=False, title="Flood Impact and Flash-Flood Hotspot Exposure")
        fig.update_xaxes(tickformat=",")
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            "This visualisation compares two flood-related indicators by state: flood evacuees in 2021 show actual human displacement during a flood event, while active flash-flood hotspots show longer-term structural flood-risk locations. "
            "The comparison helps identify states that require evacuation preparedness, drainage improvement, and targeted disaster-risk planning."
        )

        st.markdown("#### Supporting indicator — available flood-impact figures")
        trend = flood_trend.sort_values("Display_Year")
        trend_fig = px.bar(
            trend,
            x="Period",
            y="Flood_Evacuees",
            text=trend["Flood_Evacuees"].map(lambda x: f"{int(x):,}"),
            labels={"Period": "Year", "Flood_Evacuees": "Flood evacuees / victims evacuated"},
            title="Available Official Flood-Impact Figures, 2021 and 2022",
        )
        trend_fig.update_traces(
            hovertemplate="Year: %{x}<br>Flood evacuees / victims evacuated: %{y:,}<extra></extra>"
        )
        trend_fig.update_traces(textposition="outside", marker_color=AMBER)
        trend_fig.update_layout(**PLOTLY_LAYOUT, height=430, yaxis_tickformat=",")
        st.plotly_chart(trend_fig, use_container_width=True)
        st.caption(
            "The largest available official figure is 251,799 victims evacuated in 2022, as reported by NADMA. "
            "It provides broader national context than the 2021 JKM state-level sum of 110,070, but the two values come from different official sources and should not be treated as a directly comparable annual trend."
        )

    # Urban Population Growth
    with viz_tabs[3]:
        st.subheader("Population Growth and Flood Hotspot Exposure")
        st.markdown("**What this shows:** This bubble chart compares each state or federal territory’s overall population growth with its flood-hotspot exposure; bubble size represents 2023 population and colour represents region. Overall population growth is used as a proxy for urbanisation pressure.")
        fig = px.scatter(
            fstate,
            x="Flood_Hotspots",
            y="Pop_Growth_Pct",
            size="Pop_2023",
            color="Region",
            color_discrete_map=REGION_COLORS,
            size_max=55,
            hover_name="State",
            text="State" if show_state_labels else None,
            title="Population Growth and Flood Hotspot Exposure",
            custom_data=["Region", "Flood_Hotspots", "Pop_Growth_Pct", "Pop_2023"],
            labels={
                "Flood_Hotspots": "Active flash-flood hotspots",
                "Pop_Growth_Pct": "Population growth 2018–2023 (%)",
                "Pop_2023": "Population in 2023",
                "Region": "Region",
                "State": "State / territory",
            },
        )
        if show_state_labels:
            fig.update_traces(textposition="top center", textfont=dict(size=9, color=SLATE))

        fig.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Region: %{customdata[0]}<br>"
                "Active flash-flood hotspots: %{customdata[1]:,}<br>"
                "Population growth 2018–2023: %{customdata[2]:.1f}%<br>"
                "Population in 2023: %{customdata[3]:,}"
                "<extra></extra>"
            ),
            selector=dict(mode="markers+text")
        )
        fig.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "Region: %{customdata[0]}<br>"
                "Active flash-flood hotspots: %{customdata[1]:,}<br>"
                "Population growth 2018–2023: %{customdata[2]:.1f}%<br>"
                "Population in 2023: %{customdata[3]:,}"
                "<extra></extra>"
            ),
            selector=dict(mode="markers")
        )

        # Manual linear trendline. This avoids Plotly Express trendline="ols",
        # which requires the extra statsmodels package and can cause deployment/local errors.
        if show_trendline:
            trend_df = fstate[["Flood_Hotspots", "Pop_Growth_Pct"]].dropna().copy()
            if len(trend_df) >= 2 and trend_df["Flood_Hotspots"].nunique() > 1:
                x = trend_df["Flood_Hotspots"].astype(float).to_numpy()
                y = trend_df["Pop_Growth_Pct"].astype(float).to_numpy()
                slope, intercept = np.polyfit(x, y, 1)
                x_line = np.linspace(float(x.min()), float(x.max()), 100)
                y_line = slope * x_line + intercept
                fig.add_trace(
                    go.Scatter(
                        x=x_line,
                        y=y_line,
                        mode="lines",
                        name="Linear trend",
                        line=dict(color=SLATE, width=2, dash="dash"),
                        hoverinfo="skip",
                    )
                )

        fig.add_hline(y=0, line_dash="dot", line_color=SLATE)
        fig.update_layout(
            **PLOTLY_LAYOUT,
            height=560,
            xaxis_title="Active flash-flood hotspots",
            yaxis_title="Population growth 2018–2023 (%)",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            "This visualisation shows how each state or federal territory’s overall population growth from 2018 to 2023 relates to its number of active flash-flood hotspots. "
            "The bubble size represents the 2023 population, helping to identify whether larger or faster-growing urban areas are exposed to higher flood-risk locations."
        )
        if show_trendline:
            st.caption(
                "The dashed linear trendline summarises the overall direction of the relationship. "
                "In this chart, the downward slope suggests that states with more active flash-flood hotspots tend to show lower population growth, although this is an association and not a causal result."
            )

# =============================================================================
# TAB 3: SUMMARY STATISTICS
# =============================================================================
with main_tabs[2]:
    st.subheader("Summary Statistics")
    st.write(
        "The summary statistics provide a quick overview of Malaysia’s SDG 11 indicators used in this dashboard. "
        "They show the overall population level, population growth pattern, flood-impact severity, flood-hotspot exposure, and air-quality trend before interpreting the visualisations."
    )

    pm_mean = float(ap["PM_2.5"].mean()) if not ap.empty else None
    pm_min = float(ap["PM_2.5"].min()) if not ap.empty else None
    pm_max = float(ap["PM_2.5"].max()) if not ap.empty else None

    summary_rows = [
        {
            "Indicator": "National population 2023",
            "Summary value": f"{state['Pop_2023'].sum()/1e6:.2f} million",
            "Interpretation": "Shows the overall urban-planning population base.",
        },
        {
            "Indicator": "Mean population across 16 state-level areas, 2023",
            "Summary value": f"{state['Pop_2023'].mean()/1e6:.2f} million",
            "Interpretation": "Population is unevenly distributed across states and territories.",
        },
        {
            "Indicator": "Population growth 2018–2023",
            "Summary value": f"Mean {state['Pop_Growth_Pct'].mean():.2f}%; range {state['Pop_Growth_Pct'].min():.2f}% to {state['Pop_Growth_Pct'].max():.2f}%",
            "Interpretation": "Growth is uneven, with Putrajaya recording the fastest increase.",
        },
        {
            "Indicator": "Fastest state population growth",
            "Summary value": f"{fastest_row['State']} ({float(fastest_row['Pop_Growth_Pct']):+.1f}%)",
            "Interpretation": "Highlights the strongest state-level population expansion in the dataset.",
        },
        {
            "Indicator": "Highest available flood-impact figure",
            "Summary value": f"{highest_flood['Period']} ({int(highest_flood['Flood_Evacuees']):,} evacuees)",
            "Interpretation": "Shows the largest official evacuation figure in the compiled evidence; source coverage differs from the 2021 JKM state-level sum.",
        },
        {
            "Indicator": "Highest 2021 state flood evacuees",
            "Summary value": f"{highest_state_flood['State']} ({int(highest_state_flood['Flood_Evacuees_2021']):,} evacuees)",
            "Interpretation": "Shows where acute 2021 flood displacement was most concentrated.",
        },
        {
            "Indicator": "Highest flash-flood hotspots (structural risk)",
            "Summary value": f"{most_hotspots['State']} ({int(most_hotspots['Flood_Hotspots'])} hotspots)",
            "Interpretation": "Shows where recurring structural flood exposure is highest.",
        },
        {
            "Indicator": "PM2.5 2018–2022",
            "Summary value": f"Mean {pm_mean:.2f} µg/m³; range {pm_min:.2f} to {pm_max:.2f}" if pm_mean is not None else "Not available",
            "Interpretation": "PM2.5 remains above the WHO annual guideline despite the 2020 improvement.",
        },
        {
            "Indicator": "PM2.5 reduction in 2020",
            "Summary value": f"{pm_drop_pct:.0f}%" if pm_drop_pct is not None else "About −40%",
            "Interpretation": "Likely linked to reduced movement, transport and activity during COVID-19 MCO.",
        },
    ]
    summary_df = pd.DataFrame(summary_rows)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    a, b, c = st.columns(3)
    a.metric("Mean population growth", f"{state['Pop_Growth_Pct'].mean():.2f}%")
    b.metric("Mean flood hotspots", f"{state['Flood_Hotspots'].mean():.1f}")
    c.metric("Growth vs hotspot correlation", f"{corr_growth_hotspot:.2f}")

    st.markdown("#### Detailed State-Level Statistics")
    st.caption(
        "The table below provides the detailed statistical distribution of the state-level indicators. "
        "It is included as supporting evidence for readers who want to inspect the dataset more closely."
    )
    desc = state[["Pop_2023", "Pop_Growth_Pct", "Flood_Evacuees_2021", "Flood_Hotspots"]].describe().T
    desc = desc.rename(index={
        "Pop_2023": "Population in 2023",
        "Pop_Growth_Pct": "Population growth, 2018–2023 (%)",
        "Flood_Evacuees_2021": "Flood evacuees by state, 2021",
        "Flood_Hotspots": "Active flash-flood hotspots",
    })
    desc = desc.rename(columns={
        "count": "Count",
        "mean": "Mean",
        "std": "Std. dev.",
        "min": "Minimum",
        "25%": "25th percentile",
        "50%": "Median",
        "75%": "75th percentile",
        "max": "Maximum",
    })
    st.dataframe(desc.round(2), use_container_width=True)

# =============================================================================
# TAB 4: FIVE KEY INSIGHTS
# =============================================================================
with main_tabs[3]:
    st.subheader("Five Key SDG 11 Insights")
    st.write("These concise findings are written for quick lecturer review. The detailed interpretation can remain in the full report.")

    insights = [
        ("1. Concentrated population growth", "Putrajaya, Kuala Lumpur, Selangor and several northern and southern areas show comparatively strong state population growth, indicating concentrated development and service pressure."),
        ("2. Putrajaya recorded the fastest state population growth", "Putrajaya recorded +22.2% overall population growth from 2018 to 2023. The increase may be associated with its planned federal administrative-city role and green-city planning; the dataset does not establish causation."),
        ("3. PM2.5 fell sharply and remained lower", "PM2.5 fell by about 40% in 2020, coinciding with reduced movement and activity during the MCO, and remained at a lower level through 2022; however, all observed annual values exceeded the WHO guideline."),
        ("4. Flood impact and hotspots represent different risks", "Flood evacuees show actual human displacement during recorded events, while hotspots show recurring structural exposure, so both indicators are needed for disaster-resilience planning."),
        ("5. Largest available official evacuation figure", "NADMA reported 251,799 victims evacuated in 2022. This provides national context but is not directly comparable with the 2021 JKM state-level sum because source coverage and aggregation differ."),
    ]
    for title, body in insights:
        st.markdown(f"""
<div class="insight-box"><b>{title}</b><br>{body}</div>
""", unsafe_allow_html=True)

# =============================================================================
# TAB 5: DATA & EVIDENCE
# =============================================================================
with main_tabs[4]:
    st.subheader("Data & Evidence")
    st.write(
        "This section provides transparent access to the cleaned data and contextual flood evidence behind the dashboard. "
        "It supports the final assessment requirement for dataset exploration, dashboard evidence and reproducibility."
    )

    with st.expander("📋 View Sample State-Level Data Used in the Dashboard", expanded=True):
        state_display = fstate[
            [
                "State",
                "Region",
                "Pop_2018",
                "Pop_2023",
                "Pop_Growth_Pct",
                "Flood_Evacuees_2021",
                "Flood_Hotspots",
            ]
        ].rename(columns={
            "State": "State / territory",
            "Region": "Region",
            "Pop_2018": "Population 2018",
            "Pop_2023": "Population 2023",
            "Pop_Growth_Pct": "Population growth 2018–2023 (%)",
            "Flood_Evacuees_2021": "Flood evacuees 2021",
            "Flood_Hotspots": "Active flash-flood hotspots",
        })
        st.dataframe(state_display, use_container_width=True, hide_index=True)

    with st.expander("📋 View National Air-Quality and Population Trend Data"):
        national_display = national.rename(columns={
            "year": "Year",
            "National_Population": "National population",
            "PM_2.5": "PM2.5 annual mean (µg/m³)",
            "PM_10": "PM10 annual mean (µg/m³)",
        })
        st.dataframe(national_display, use_container_width=True, hide_index=True)

    with st.expander("🌊 View Flood-Impact Period Data Source"):
        flood_display = flood_trend.rename(columns={
            "Period": "Year",
            "Display_Year": "Display year",
            "Flood_Evacuees": "Flood evacuees",
            "Source": "Data source",
            "Data_Level": "Data level",
            "Notes": "Notes",
        })
        st.dataframe(flood_display, use_container_width=True, hide_index=True)

    st.download_button(
        "Download filtered state-level data as CSV",
        fstate.to_csv(index=False).encode("utf-8"),
        file_name="filtered_state_profile.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download summary statistics as CSV",
        summary_df.to_csv(index=False).encode("utf-8"),
        file_name="dashboard_summary_statistics.csv",
        mime="text/csv",
    )

st.caption("MCI1044 Data Visualisation Final Assessment | SDG 11 Malaysia Dashboard")
