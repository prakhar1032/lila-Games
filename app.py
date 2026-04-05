import streamlit as st
import pandas as pd
import pyarrow.parquet as pq
import os
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings("ignore")

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="LILA BLACK — Player Journey Viz",
    page_icon="🎮",
    layout="wide"
)

# ---------------------------
# CUSTOM CSS
# ---------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');
    html, body, [class*="css"] { background-color: #0a0e14; color: #c9d1d9; font-family: 'Rajdhani', sans-serif; }
    .stApp { background-color: #0a0e14; }
    h1 { font-family: 'Rajdhani', sans-serif; font-weight: 700; font-size: 2rem; color: #e6c84a;
         letter-spacing: 3px; text-transform: uppercase; border-bottom: 2px solid #e6c84a33; padding-bottom: 8px; }
    .stSelectbox label, .stSlider label, .stCheckbox label, .stMultiSelect label {
        font-family: 'Share Tech Mono', monospace; color: #7aaccc; font-size: 0.75rem;
        letter-spacing: 2px; text-transform: uppercase; }
    .stSelectbox > div > div { background-color: #111820; border: 1px solid #2a3a4a; color: #c9d1d9; border-radius: 4px; }
    .metric-box { background: #111820; border: 1px solid #2a3a4a; border-left: 3px solid #e6c84a;
                  padding: 12px 16px; border-radius: 4px; font-family: 'Share Tech Mono', monospace;
                  font-size: 0.8rem; margin-bottom: 8px; }
    .metric-box span { color: #e6c84a; font-size: 1.3rem; font-weight: bold; display: block; }
    .section-label { font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: #7aaccc;
                     letter-spacing: 3px; text-transform: uppercase; margin-bottom: 6px; margin-top: 14px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# MAP CONFIG — from README (exact values)
# ---------------------------
MAP_CONFIG = {
    "AmbroseValley": {"image": "minimaps/AmbroseValley_Minimap.png", "scale": 900,  "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"image": "minimaps/GrandRift_Minimap.png",     "scale": 581,  "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"image": "minimaps/Lockdown_Minimap.jpg",      "scale": 1000, "origin_x": -500, "origin_z": -500},
}

# ---------------------------
# COORDINATE CONVERSION — exact formula from README
# ---------------------------
def world_to_pixel(x, z, cfg):
    u = (x - cfg["origin_x"]) / cfg["scale"]
    v = (z - cfg["origin_z"]) / cfg["scale"]
    return u * 1024, (1 - v) * 1024

# ---------------------------
# LOAD DATA — reads all February_XX folders inside data/
# ---------------------------
@st.cache_data
def load_all_data(base_folder="data"):
    frames = []
    for folder in sorted(os.listdir(base_folder)):
        folder_path = os.path.join(base_folder, folder)
        if not os.path.isdir(folder_path):
            continue
        for f in os.listdir(folder_path):
            try:
                path = os.path.join(folder_path, f)
                df = pq.read_table(path).to_pandas()
                df["date"] = folder   # e.g. "February_10"
                frames.append(df)
            except:
                continue
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df["event"] = df["event"].apply(lambda x: x.decode("utf-8") if isinstance(x, bytes) else x)
    df["is_bot"] = df["user_id"].apply(lambda x: str(x).isdigit())
    df["ts"] = pd.to_numeric(df["ts"], errors="coerce")
    return df

with st.spinner("📂 Loading match data..."):
    df = load_all_data("data")

if df.empty:
    st.error("❌ No data loaded. Make sure data/February_XX folders exist.")
    st.stop()

# ---------------------------
# HEADER
# ---------------------------
st.markdown("# 🎮 LILA BLACK — Player Journey Visualization")

# ---------------------------
# SIDEBAR FILTERS
# ---------------------------
with st.sidebar:
    st.markdown("## ⬡ Filters")

    st.markdown('<div class="section-label">Map</div>', unsafe_allow_html=True)
    map_selected = st.selectbox("Map", sorted(df["map_id"].unique()), label_visibility="collapsed")

    st.markdown('<div class="section-label">Date</div>', unsafe_allow_html=True)
    dates_available = sorted(df[df["map_id"] == map_selected]["date"].unique())
    date_selected = st.selectbox("Date", ["All Dates"] + dates_available, label_visibility="collapsed")

    # Filter by date first
    if date_selected == "All Dates":
        map_df = df[df["map_id"] == map_selected]
    else:
        map_df = df[(df["map_id"] == map_selected) & (df["date"] == date_selected)]

    st.markdown('<div class="section-label">Match</div>', unsafe_allow_html=True)
    match_options = sorted(map_df["match_id"].unique())
    match_selected = st.selectbox("Match", match_options, label_visibility="collapsed",
                                  format_func=lambda x: x[:30] + "...")

    st.markdown("---")
    st.markdown("## ⬡ Overlays")
    show_traffic_hm = st.checkbox("Traffic Heatmap",  value=True)
    show_kills_hm   = st.checkbox("Kill Zone Heatmap",  value=False)
    show_deaths_hm  = st.checkbox("Death Zone Heatmap", value=False)
    show_paths      = st.checkbox("Player Paths",        value=True)
    show_events     = st.checkbox("Event Markers",       value=True)

    st.markdown("---")
    st.markdown("## ⬡ Players")
    show_humans = st.checkbox("Show Humans", value=True)
    show_bots   = st.checkbox("Show Bots",   value=True)

# ---------------------------
# FILTER TO SELECTED MATCH
# ---------------------------
filtered = df[
    (df["map_id"] == map_selected) &
    (df["match_id"] == match_selected)
].copy()

if not show_humans:
    filtered = filtered[filtered["is_bot"] == True]
if not show_bots:
    filtered = filtered[filtered["is_bot"] == False]

if filtered.empty:
    st.warning("⚠️ No data for this selection.")
    st.stop()

# ---------------------------
# APPLY COORDINATE CONVERSION
# ---------------------------
cfg = MAP_CONFIG[map_selected]

coords = filtered.apply(lambda row: world_to_pixel(row["x"], row["z"], cfg), axis=1)
filtered["px"] = coords.apply(lambda c: c[0])
filtered["py"] = coords.apply(lambda c: c[1])

# Keep only points within minimap bounds
filtered = filtered[
    (filtered["px"] >= 0) & (filtered["px"] <= 1024) &
    (filtered["py"] >= 0) & (filtered["py"] <= 1024)
].copy()

# ---------------------------
# METRICS ROW
# ---------------------------
total_players  = filtered["user_id"].nunique()
human_count    = filtered[~filtered["is_bot"]]["user_id"].nunique()
bot_count      = filtered[filtered["is_bot"]]["user_id"].nunique()
kill_count     = len(filtered[filtered["event"] == "Kill"])
death_count    = len(filtered[filtered["event"].isin(["Killed", "KilledByStorm"])])
loot_count     = len(filtered[filtered["event"] == "Loot"])

c1, c2, c3, c4, c5, c6 = st.columns(6)
for col, label, val in zip(
    [c1,c2,c3,c4,c5,c6],
    ["Players","Humans","Bots","Kills","Deaths","Loots"],
    [total_players, human_count, bot_count, kill_count, death_count, loot_count]
):
    col.markdown(f'<div class="metric-box">{label}<span>{val}</span></div>', unsafe_allow_html=True)

# ---------------------------
# SMOOTH HEATMAP HELPER
# ---------------------------
def make_smooth_heatmap(px, py, sigma=20, bins=256):
    h, _, _ = np.histogram2d(px, py, bins=bins, range=[[0,1024],[0,1024]])
    h = gaussian_filter(h.T, sigma=sigma)
    if h.max() > 0:
        h /= h.max()
    return h

# ---------------------------
# EVENT STYLES
# ---------------------------
EVENT_STYLE = {
    "Kill":          {"color": "#ff4d4d", "marker": "x",  "size": 60,  "lw": 1.8, "zorder": 7, "label": "Kill"},
    "Killed":        {"color": "#ffffff", "marker": "v",  "size": 45,  "lw": 1.2, "zorder": 7, "label": "Death"},
    "BotKill":       {"color": "#ff944d", "marker": "x",  "size": 40,  "lw": 1.2, "zorder": 6, "label": "Bot Kill"},
    "BotKilled":     {"color": "#aaaaaa", "marker": "v",  "size": 35,  "lw": 1.0, "zorder": 6, "label": "Bot Death"},
    "Loot":          {"color": "#f5c842", "marker": "*",  "size": 70,  "lw": 1.0, "zorder": 6, "label": "Loot"},
    "KilledByStorm": {"color": "#bf5fff", "marker": "D",  "size": 50,  "lw": 1.2, "zorder": 7, "label": "Storm Kill"},
    "Position":      {"color": "#39ff14", "marker": ".",  "size": 3,   "lw": 0.5, "zorder": 4, "label": "Human Pos"},
    "BotPosition":   {"color": "#00cfff", "marker": ".",  "size": 3,   "lw": 0.5, "zorder": 4, "label": "Bot Pos"},
}

# ---------------------------
# DRAW MAP
# ---------------------------
def draw_map(data, title=""):
    img = Image.open(cfg["image"]).convert("RGBA")
    fig, ax = plt.subplots(figsize=(9, 9), facecolor="#0a0e14")
    ax.set_facecolor("#0a0e14")
    ax.imshow(img, extent=[0, 1024, 1024, 0], zorder=1)

    # Traffic heatmap
    if show_traffic_hm and len(data) > 10:
        hm = make_smooth_heatmap(data["px"], data["py"])
        masked = np.ma.masked_where(hm < 0.02, hm)
        ax.imshow(masked, extent=[0,1024,1024,0], cmap="plasma",
                  alpha=0.42, zorder=2, aspect="auto", interpolation="bilinear")

    # Kill heatmap
    if show_kills_hm:
        kdf = data[data["event"] == "Kill"]
        if len(kdf) > 2:
            hm_k = make_smooth_heatmap(kdf["px"], kdf["py"], sigma=25)
            masked_k = np.ma.masked_where(hm_k < 0.05, hm_k)
            ax.imshow(masked_k, extent=[0,1024,1024,0], cmap="Reds",
                      alpha=0.55, zorder=3, aspect="auto", interpolation="bilinear")

    # Death heatmap
    if show_deaths_hm:
        ddf = data[data["event"].isin(["Killed","KilledByStorm"])]
        if len(ddf) > 2:
            hm_d = make_smooth_heatmap(ddf["px"], ddf["py"], sigma=25)
            masked_d = np.ma.masked_where(hm_d < 0.05, hm_d)
            ax.imshow(masked_d, extent=[0,1024,1024,0], cmap="Blues",
                      alpha=0.50, zorder=3, aspect="auto", interpolation="bilinear")

    # Player paths
    if show_paths:
        for pid in data["user_id"].unique():
            pdata = data[
                (data["user_id"] == pid) &
                (data["event"].isin(["Position","BotPosition"]))
            ].sort_values("ts")
            if len(pdata) > 1:
                color = "#00cfff" if pdata["is_bot"].iloc[0] else "#39ff14"
                ax.plot(pdata["px"], pdata["py"], color=color,
                        linewidth=0.9, alpha=0.35, zorder=5, solid_capstyle="round")

    # Event markers
    if show_events:
        for event, style in EVENT_STYLE.items():
            subset = data[data["event"] == event]
            if not subset.empty:
                ax.scatter(subset["px"], subset["py"],
                           c=style["color"], marker=style["marker"],
                           s=style["size"], linewidths=style["lw"],
                           zorder=style["zorder"], alpha=0.92)

    # Legend
    legend_elements = [
        Line2D([0],[0], color="#39ff14", lw=2, label="Human Path"),
        Line2D([0],[0], color="#00cfff", lw=2, label="Bot Path"),
        Line2D([0],[0], marker="x", color="#ff4d4d", linestyle="None", ms=8, label="Kill"),
        Line2D([0],[0], marker="v", color="#ffffff", linestyle="None", ms=7, label="Death"),
        Line2D([0],[0], marker="*", color="#f5c842", linestyle="None", ms=9, label="Loot"),
        Line2D([0],[0], marker="D", color="#bf5fff", linestyle="None", ms=7, label="Storm Kill"),
        Line2D([0],[0], marker="x", color="#ff944d", linestyle="None", ms=7, label="Bot Kill"),
    ]
    leg = ax.legend(handles=legend_elements, loc="upper right",
                    framealpha=0.88, facecolor="#0d1117", edgecolor="#2a3a4a",
                    labelcolor="#c9d1d9", fontsize=8,
                    title="LEGEND", title_fontsize=7)
    leg.get_title().set_color("#e6c84a")

    ax.set_xlim(0, 1024)
    ax.set_ylim(1024, 0)
    ax.axis("off")
    ax.set_title(title, color="#e6c84a", fontsize=9, fontfamily="monospace", loc="left", pad=8)
    return fig

with st.spinner("🗺️ Loading map..."):
    fig = draw_map(filtered, title=f"{map_selected}  ·  {match_selected[:35]}...")
st.pyplot(fig, use_container_width=True)

# ---------------------------
# TIMELINE PLAYBACK
# ---------------------------
st.markdown("---")
st.markdown('<div class="section-label">⬡ Timeline Playback</div>', unsafe_allow_html=True)

if filtered["ts"].notna().any():
    ts_min = int(filtered["ts"].min())
    ts_max = int(filtered["ts"].max())

    if ts_max > ts_min:
        ts_range = st.slider(
            "Time window (ms)",
            min_value=ts_min, max_value=ts_max,
            value=(ts_min, ts_max),
            label_visibility="visible"
        )
        slice_df = filtered[(filtered["ts"] >= ts_range[0]) & (filtered["ts"] <= ts_range[1])]
        st.markdown(f'<div class="section-label">Events in window: {len(slice_df)}</div>', unsafe_allow_html=True)
        with st.spinner("⏱️ Rendering timeline..."):
            fig2 = draw_map(slice_df, title=f"Timeline: {ts_range[0]:,} → {ts_range[1]:,} ms  |  Events: {len(slice_df)}")
            st.pyplot(fig2, use_container_width=True)

# ---------------------------
# DEBUG (collapsible)
# ---------------------------
with st.expander("🔍 Debug Info"):
    st.write(f"Events in match: {len(filtered)}")
    st.write(f"PX range: {filtered['px'].min():.1f} → {filtered['px'].max():.1f}")
    st.write(f"PY range: {filtered['py'].min():.1f} → {filtered['py'].max():.1f}")
    st.write(filtered["event"].value_counts())