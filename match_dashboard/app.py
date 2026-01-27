import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore
import sys
import os

# 1. SETUP PATHS
# If your app is in 'match_dashboard' and physics is in 'utils'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.physics import (
    get_distance_percentages, 
    get_player_card_stats, 
    get_team_physicals_surgical
)

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pro-Match Analytics", layout="wide", page_icon="⚽")

# --- DATA LOADING (SUPER FAST) ---
@st.cache_data
def load_dashboard_data():
    # Load the files you already ran prepare_player_data on in your Notebook
    df_h = pd.read_pickle('../DATASETS/Cleaned/Home_Tracking_Clean.pkl')
    df_a = pd.read_pickle('../DATASETS/Cleaned/Away_Tracking_Clean.pkl')
    return df_h, df_a

df_home, df_away = load_dashboard_data()

# --- SIDEBAR ---
st.sidebar.header("Match Control")
team_choice = st.sidebar.radio("Select Team", ["Home", "Away"])
df_current = df_home if team_choice == "Home" else df_away

# Get player list from the columns you already created (ending in _speed)
player_ids = sorted([c.split('_')[1] for c in df_current.columns if '_speed' in c], key=int)
selected_player = st.sidebar.selectbox("Select Player", player_ids)

# --- TOP ROW: PRE-CALCULATED METRICS ---
# These functions now run instantly because the columns already exist
stats = get_player_card_stats(df_current, selected_player, team_choice)

m1, m2, m3 = st.columns(3)
m1.metric("Total Distance", stats["Total Distance"])
m2.metric("Top Speed", stats["Top Speed"])
m3.metric("Sprints (>25.2 km/h)", stats["Sprints"])

st.markdown("---")

# --- MIDDLE ROW: CHARTS ---
col_left, col_right = st.columns([1, 1.5])

with col_left:
    st.subheader("Work Rate Distribution")
    zone_data = get_distance_percentages(df_current, selected_player, team_choice)
    fig_pie = px.pie(
        names=list(zone_data.keys()), 
        values=list(zone_data.values()),
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.Greens_r
    )
    st.plotly_chart(fig_pie, width='stretch')

with col_right:
    st.subheader("Team Rankings")
    leaderboard = get_team_physicals_surgical(df_current, team_choice)
    st.dataframe(leaderboard, width='stretch', hide_index=True)

# --- BOTTOM ROW: HIGH-PERFORMANCE WEBGL CHART ---
st.markdown("---")
st.subheader(f"Speed Profile: Player {selected_player}")

speed_series = df_current[f"{team_choice}_{selected_player}_speed"]

# This uses Scattergl (WebGL) to prevent the "WebSocket Closed" error
fig_speed = go.Figure(data=go.Scattergl(
    y=speed_series.values,
    mode='lines',
    line=dict(color='#2ecc71', width=1.5)
))

fig_speed.update_layout(
    xaxis_title="Frame",
    yaxis_title="Speed (km/h)",
    margin=dict(l=20, r=20, t=20, b=20),
    height=350
)

st.plotly_chart(fig_speed, width='stretch')