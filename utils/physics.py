import numpy as np # type: ignore
import pandas as pd # type: ignore
from scipy.signal import savgol_filter # type: ignore
import plotly.express as px # type: ignore
import plotly.graph_objects as go # type: ignore

def prepare_player_data(df, team_label='Home'):
    DT = 0.04
    x_cols = [c for c in df.columns if c.lower().endswith('_x') and team_label.lower() in c.lower()]
    
    for x_col in x_cols:
        y_col = x_col[:-1] + ('Y' if x_col.endswith('_X') else 'y')
        # Robust ID extraction
        player_id = x_col.replace('_X','').replace('_x','').replace(f'{team_label}_','').strip()
        
        if 'ball' in player_id.lower(): continue

        # 1. Distance Calculation
        dist_m = np.sqrt(df[x_col].diff()**2 + df[y_col].diff()**2).fillna(0)
        
        # 2. Surgical Cleaning
        raw_speed_kmh = (dist_m / DT) * 3.6
        q95 = raw_speed_kmh.quantile(0.95)
        clean_speed = raw_speed_kmh.clip(upper=q95 * 1.5)
        
        # 3. Smooth with high-quality filters
        smooth_median = clean_speed.rolling(window=31, center=True).median().fillna(0)
        final_speed = savgol_filter(smooth_median, 21, 3) 
        
        # 4. Save back to df
        df[f'{team_label}_{player_id}_dist'] = dist_m
        df[f'{team_label}_{player_id}_speed'] = final_speed
    
    return df

def get_distance_percentages(df, player_id, team_label='Home'):
    speed = df[f'{team_label}_{player_id}_speed']
    dist = df[f'{team_label}_{player_id}_dist']
    total_dist = dist.sum()
    
    if total_dist == 0:
        return {zone: 0.0 for zone in ['Walking', 'Jogging', 'Running', 'HSR', 'Sprinting']}
    
    zones = {'Walking': (0, 7), 'Jogging': (7, 15), 'Running': (15, 20), 'HSR': (20, 25), 'Sprinting': (25, 100)}
    
    zone_percentages = {}
    for zone, (low, high) in zones.items():
        mask = (speed >= low) & (speed < high)
        zone_percentages[zone] = np.round((dist[mask].sum() / total_dist) * 100, 2)
        
    return zone_percentages

def get_player_card_stats(df, player_id, team_label='Home'):
    speed_col = f'{team_label}_{player_id}_speed'
    dist_col = f'{team_label}_{player_id}_dist'
    
    return {
        "Total Distance": f"{np.round(df[dist_col].sum() / 1000, 2)} km",
        "Top Speed": f"{np.round(df[speed_col].max(), 2)} km/h",
        
    }

def get_team_physicals_surgical(df, team_label='Home'):
    """Summarizes all players into a single dataframe for the leaderboard"""
    summary_data = []
    # Identify players by looking at the speed columns we created
    speed_cols = [c for c in df.columns if c.startswith(f"{team_label}_") and c.endswith("_speed")]
    
    for col in speed_cols:
        player_id = col.split('_')[1]
        dist_col = f"{team_label}_{player_id}_dist"
        
        summary_data.append({
            'Full ID': f"{team_label}_{player_id}",
            'Total Distance (km)': np.round(df[dist_col].sum() / 1000, 2),
            'Top Speed (km/h)': np.round(df[col].max(), 2)
        })

    return pd.DataFrame(summary_data)








def get_player_heatmap(df, player_id, team_label='Home'):
    # 1. Column Selection
    x_col = next((c for c in df.columns if c.lower() == f"{team_label}_{player_id}_x".lower()), None)
    y_col = next((c for c in df.columns if c.lower() == f"{team_label}_{player_id}_y".lower()), None)
    
    if not x_col or not y_col:
        return go.Figure().update_layout(title="No Position Data Found", template="dark")

    # 2. Extract Data
    df_temp = df[[x_col, y_col]].copy().dropna()
    
    # --- HALFTIME FLIP LOGIC ---
    # We detect the second half based on the 'Period' column if it exists, 
    # or by splitting the dataframe in half.
    if 'Period' in df.columns:
        # Flip only if Period is 2
        df_temp.loc[df['Period'] == 2, x_col] *= -1
        df_temp.loc[df['Period'] == 2, y_col] *= -1
    else:
        # Fallback: Split by the middle index of the match
        mid_point = len(df_temp) // 2
        df_temp.iloc[mid_point:, 0] *= -1 # Flip X
        df_temp.iloc[mid_point:, 1] *= -1 # Flip Y
    # ---------------------------

    # Downsample for performance
    df_sub = df_temp.iloc[::10]
    x_data = df_sub[x_col].values
    y_data = df_sub[y_col].values

    # 3. Create the Figure
    fig = go.Figure()

    # Glowing Contour Heatmap
    fig.add_trace(go.Histogram2dContour(
        x=x_data,
        y=y_data,
        ncontours=40,
        colorscale='Hot', 
        showscale=False,
        contours=dict(coloring='heatmap', showlines=False),
        line=dict(width=0)
    ))

    # 4. Styling the Pitch (Centered at 0,0)
    line_style = dict(color="rgba(255, 255, 255, 0.4)", width=2)
    
    # Outer boundaries
    fig.add_shape(type="rect", x0=-53, y0=-34, x1=53, y1=34, line=line_style)
    # Midfield line and Center Circle
    fig.add_shape(type="line", x0=0, y0=-34, x1=0, y1=34, line=line_style)
    fig.add_shape(type="circle", x0=-9.15, y0=-9.15, x1=9.15, y1=9.15, line=line_style)
    # Penalty boxes
    fig.add_shape(type="rect", x0=-53, y0=-20, x1=-36.5, y1=20, line=line_style)
    fig.add_shape(type="rect", x0=36.5, y0=-20, x1=53, y1=20, line=line_style)

    # 5. Add Attack Arrow (To show direction is now standardized)
    fig.add_annotation(
        x=20, y=38, text="ATTACK DIRECTION",
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2,
        arrowcolor="white", font=dict(color="white", size=10)
    )

    # 6. Layout Configuration
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        xaxis=dict(range=[-55, 55], visible=False),
        yaxis=dict(range=[-40, 40], visible=False), # Slightly wider to fit the arrow
        margin=dict(l=10, r=10, t=10, b=10),
        height=500
    )

    return fig