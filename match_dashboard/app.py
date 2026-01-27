import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# --- 1. SYSTEM SETUP ---
# Ensure Python can find the 'utils' folder for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.physics import (
    get_distance_percentages, 
    get_player_card_stats, 
    get_team_physicals_surgical,
    get_player_heatmap
)

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Player Performance", layout="wide", page_icon="⚽")

# Custom CSS for the circular player badge (Replacement for display picture)
st.markdown("""
    <style>
    .player-badge {
        height: 100px; width: 100px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 40px; font-weight: bold;
        margin-bottom: 10px; border: 4px solid #f0f2f6;
    }
    .home-color { background-color: #ff4b4b; } /* Red for Home */
    .away-color { background-color: #0068c9; } /* Blue for Away */
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING ---
@st.cache_data
def load_dashboard_data():
    """Loads pre-processed tracking data from your Notebook exports."""
    # Ensure these paths match your saved file names exactly
    home_path = '../DATASETS/Cleaned/Home_Tracking_Clean.pkl'
    away_path = '../DATASETS/Cleaned/Away_Tracking_Clean.pkl'
    
    if os.path.exists(home_path) and os.path.exists(away_path):
        df_h = pd.read_pickle(home_path)
        df_a = pd.read_pickle(away_path)
        return df_h, df_a
    return None, None

df_home, df_away = load_dashboard_data()

# --- 4. MAIN APP LOGIC ---
if df_home is not None and df_away is not None:
    # Sidebar for Team and Player selection
    st.sidebar.header("Match Control")
    team_choice = st.sidebar.radio("Select Team", ["Home", "Away"])
    df_current = df_home if team_choice == "Home" else df_away

    # Extracting Player IDs from column names (Format: Team_ID_speed)
    player_ids = sorted([c.split('_')[1] for c in df_current.columns if '_speed' in c], key=int)
    selected_id = st.sidebar.selectbox("Select Player", player_ids)

    # --- 5. PLAYER HEADER (SOFASCORE STYLE) ---
    col_avatar, col_name = st.columns([1, 5])
    
    with col_avatar:
        # Dynamic Badge color based on team choice
        badge_class = "home-color" if team_choice == "Home" else "away-color"
        st.markdown(f'<div class="player-badge {badge_class}">{selected_id}</div>', unsafe_allow_html=True)
        
    with col_name:
        st.title(f"Player {selected_id}")
        st.markdown(f"**{team_choice} Team**")
        
        # Calculating minutes played (Assuming 25 fps)
        total_frames = len(df_current)
        mins_played = round(total_frames / (25 * 60))
        st.subheader(f"⏱️ Minutes played: {mins_played}'")

    st.markdown("---")

    # --- 6. CORE PHYSICAL STATS (METRICS) ---
    stats = get_player_card_stats(df_current, selected_id, team_choice)
    m1, m2 = st.columns(2)
    
    m1.metric("Total Distance", stats["Total Distance"])
    m2.metric("Top Speed", stats["Top Speed"])
    

    st.markdown("---")

    # --- 7. COLLAPSIBLE ANALYTICS SECTIONS ---
    
    # HEATMAP DROP-DOWN
    with st.expander("⚽ Match Heatmap", expanded=False):
        st.write("### Positional Density ")
        # This calls your high-res glow function from physics.py
        fig_heat = get_player_heatmap(df_current, selected_id, team_choice)
        st.plotly_chart(fig_heat, width='stretch')

    # WORK RATE DROP-DOWN
    with st.expander("📊 Work Rate Distribution", expanded=False):
        st.write("### Distance by Intensity Zone")
        zone_data = get_distance_percentages(df_current, selected_id, team_choice)
        fig_pie = px.pie(
            names=list(zone_data.keys()), 
            values=list(zone_data.values()),
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Greens_r
        )
        st.plotly_chart(fig_pie, width='stretch')

    st.markdown("---")

    # --- 8. TEAM RANKINGS TABLE ---
    st.markdown("### 🏆 Team Performance Leaderboard")
    leaderboard = get_team_physicals_surgical(df_current, team_choice)
    st.dataframe(
        leaderboard.sort_values("Total Distance (km)", ascending=False), 
        width='stretch', 
        hide_index=True
    )

else:
    # Error handling if files are missing or paths are wrong
    st.error("🚨 Data files not found!")
    st.info(f"Looking in: {os.path.abspath('../DATASETS/Cleaned/')}")
    st.stop()