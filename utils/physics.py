import numpy as np # type: ignore
import pandas as pd # type: ignore
from scipy.signal import savgol_filter # type: ignore

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
        "Sprints": len(df[df[speed_col] > 25.2]) // 25 
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