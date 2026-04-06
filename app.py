import streamlit as st
import pyarrow.parquet as pq
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import Counter
from pathlib import Path

st.set_page_config(page_title="LILA BLACK - Player Journey Tool", layout="wide")

# --------------------------------------------------
# HERO BANNER (URL-BASED)
# --------------------------------------------------
hero_html = """
<div style="
    width: 100%;
    border-radius: 24px;
    overflow: hidden;
    margin-bottom: 28px;
    position: relative;
    box-shadow: 0 12px 36px rgba(0,0,0,0.35);
    background: #0f172a;
">
    <div style="
        position: relative;
        width: 100%;
        height: 340px;
        overflow: hidden;
    ">
        <img src="https://pub-1407f82391df4ab1951418d04be76914.r2.dev/uploads/0aaeb101-419c-4b86-8227-e79a15cdb970.png"
             style="
                width: 100%;
                height: 100%;
                object-fit: cover;
                object-position: center center;
                display: block;
                filter: brightness(0.62);
             ">
        <div style="
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, rgba(2,6,23,0.82) 0%, rgba(2,6,23,0.48) 45%, rgba(2,6,23,0.12) 100%);
        "></div>
        <div style="
            position: absolute;
            left: 48px;
            bottom: 34px;
            color: white;
            max-width: 760px;
        ">
            <h1 style="margin: 0; font-size: 56px; line-height: 1.02; font-weight: 800;">
                LILA BLACK
            </h1>
            <h2 style="margin: 10px 0 0 0; font-size: 30px; line-height: 1.18; font-weight: 650;">
                Player Journey Visualization Tool
            </h2>
            <p style="margin: 16px 0 0 0; font-size: 18px; opacity: 0.95;">
                Explore player movement, combat zones, loot clusters, storm impact, and match progression.
            </p>
        </div>
    </div>
</div>
"""

st.markdown("""
<style>
/* Main page */
.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #111827 45%, #172033 100%);
    color: #e5e7eb;
}

/* Top header */
header[data-testid="stHeader"] {
    background: transparent !important;
    border-bottom: none !important;
}

[data-testid="stToolbar"] {
    right: 1rem;
}

/* Main content */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* Select control */
div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.05) !important;
    border-color: rgba(255,255,255,0.12) !important;
    color: #e5e7eb !important;
}

/* Dropdown popup */
div[role="listbox"] {
    background-color: #111827 !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
}

/* Dropdown options */
div[role="option"] {
    background-color: #111827 !important;
    color: #e5e7eb !important;
}

/* Hover */
div[role="option"]:hover {
    background-color: #1f2937 !important;
    color: #ffffff !important;
}

/* Selected option */
li[aria-selected="true"],
div[aria-selected="true"] {
    background-color: #374151 !important;
    color: #ffffff !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 12px 16px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.18);
}

/* Tables */
div.stDataFrame, div[data-testid="stTable"] {
    border-radius: 14px;
    overflow: hidden;
    background: rgba(255,255,255,0.03);
}

/* Expanders */
details {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 4px 10px;
}

/* Captions */
[data-testid="stCaptionContainer"] {
    color: #cbd5e1 !important;
}

table {
    color: #e5e7eb !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown(hero_html, unsafe_allow_html=True)

# --------------------------------------------------
# PATHS
# --------------------------------------------------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "Data" / "player_data"
MINIMAP_DIR = DATA_DIR / "minimaps"

# --------------------------------------------------
# MAP CONFIG
# --------------------------------------------------
MAP_CONFIG = {
    "AmbroseValley": {
        "scale": 900,
        "origin_x": -370,
        "origin_z": -473,
        "image": MINIMAP_DIR / "AmbroseValley_Minimap.png",
    },
    "GrandRift": {
        "scale": 581,
        "origin_x": -290,
        "origin_z": -290,
        "image": MINIMAP_DIR / "GrandRift_Minimap.png",
    },
    "Lockdown": {
        "scale": 1000,
        "origin_x": -500,
        "origin_z": -500,
        "image": MINIMAP_DIR / "Lockdown_Minimap.jpg",
    },
}

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def decode_event(x):
    return x.decode("utf-8") if isinstance(x, bytes) else x

def is_bot(user_id):
    return "-" not in str(user_id)

def world_to_map(df, map_name):
    cfg = MAP_CONFIG[map_name]
    df = df.copy()
    df["u"] = (df["x"] - cfg["origin_x"]) / cfg["scale"]
    df["v"] = (df["z"] - cfg["origin_z"]) / cfg["scale"]
    df["px"] = df["u"] * 1024
    df["py"] = (1 - df["v"]) * 1024
    return df

@st.cache_data
def get_date_folders():
    folders = []
    for item in DATA_DIR.iterdir():
        if item.is_dir() and item.name != "minimaps":
            folders.append(item.name)
    return sorted(folders)

@st.cache_data
def get_match_summary(selected_date):
    folder_path = DATA_DIR / selected_date
    match_counts = Counter()
    match_map = {}
    match_kills = Counter()
    match_deaths = Counter()
    match_storm = Counter()

    for file in os.listdir(folder_path):
        try:
            parts = file.split("_", 1)
            if len(parts) < 2:
                continue

            match_id = parts[1]
            match_counts[match_id] += 1

            file_path = folder_path / file
            table = pq.read_table(file_path)
            temp_df = table.to_pandas()
            temp_df["event"] = temp_df["event"].apply(decode_event)

            if not temp_df.empty and "map_id" in temp_df.columns:
                match_map[match_id] = str(temp_df["map_id"].iloc[0])

            match_kills[match_id] += len(temp_df[temp_df["event"].isin(["Kill", "BotKill"])])
            match_deaths[match_id] += len(temp_df[temp_df["event"].isin(["Killed", "BotKilled"])])
            match_storm[match_id] += len(temp_df[temp_df["event"] == "KilledByStorm"])

        except:
            continue

    rows = []
    for match_id, count in match_counts.items():
        kills = match_kills.get(match_id, 0)
        deaths = match_deaths.get(match_id, 0)
        storm_deaths = match_storm.get(match_id, 0)

        rows.append(
            {
                "match_id": match_id,
                "player_files": count,
                "map_id": match_map.get(match_id, "Unknown"),
                "kills": kills,
                "deaths": deaths,
                "storm_deaths": storm_deaths,
                "combat_score": kills + deaths + storm_deaths,
            }
        )

    summary_df = pd.DataFrame(rows)
    if not summary_df.empty:
        summary_df = summary_df.sort_values(
            by=["combat_score", "player_files"],
            ascending=False
        )

    return summary_df

@st.cache_data
def load_match_data(selected_date, selected_match):
    folder_path = DATA_DIR / selected_date
    all_data = []

    for file in os.listdir(folder_path):
        if selected_match in file:
            try:
                file_path = folder_path / file
                table = pq.read_table(file_path)
                temp_df = table.to_pandas()
                temp_df["event"] = temp_df["event"].apply(decode_event)
                all_data.append(temp_df)
            except:
                continue

    if not all_data:
        return pd.DataFrame()

    df = pd.concat(all_data, ignore_index=True)
    df["user_type"] = df["user_id"].apply(lambda x: "Bot" if is_bot(x) else "Human")
    return df

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.header("Filters")

date_folders = get_date_folders()
if not date_folders:
    st.error("No date folders found inside Data/player_data")
    st.stop()

selected_date = st.sidebar.selectbox("Select Date", date_folders)

summary_df = get_match_summary(selected_date)
if summary_df.empty:
    st.warning("No matches found for selected date.")
    st.stop()

map_options = ["All"] + sorted(summary_df["map_id"].dropna().unique().tolist())
selected_map = st.sidebar.selectbox("Select Map", map_options)

min_players = st.sidebar.slider("Minimum player files in match", 1, 20, 8)

filtered_summary = summary_df.copy()
filtered_summary = filtered_summary[filtered_summary["player_files"] >= min_players]

if selected_map != "All":
    filtered_summary = filtered_summary[filtered_summary["map_id"] == selected_map]

if filtered_summary.empty:
    st.warning("No matches found with the selected filters.")
    st.stop()

match_options = filtered_summary["match_id"].tolist()
default_match_index = 0
if len(filtered_summary) > 0:
    best_match = filtered_summary.iloc[0]["match_id"]
    default_match_index = match_options.index(best_match)

selected_match = st.sidebar.selectbox("Select Match", match_options, index=default_match_index)
st.sidebar.caption("Matches are ranked by combat activity first, then player count.")

show_kills = st.sidebar.checkbox("Show Kill markers", True)
show_deaths = st.sidebar.checkbox("Show Death markers", True)
show_loot = st.sidebar.checkbox("Show Loot markers", True)
show_storm = st.sidebar.checkbox("Show Storm Death markers", True)
show_heatmap = st.sidebar.checkbox("Show Heatmaps", True)

# --------------------------------------------------
# LOAD MATCH
# --------------------------------------------------
df = load_match_data(selected_date, selected_match)

if df.empty:
    st.error("Unable to load match data.")
    st.stop()

df = df.sort_values("ts").copy()

# --------------------------------------------------
# TIMELINE
# --------------------------------------------------
st.subheader("⏱️ Match Timeline")

min_ts = df["ts"].min()
max_ts = df["ts"].max()

timeline_percent = st.slider("Timeline Playback (%)", 0, 100, 100)
current_ts = min_ts + (max_ts - min_ts) * (timeline_percent / 100)

st.write("Showing events up to:", current_ts)

df = df[df["ts"] <= current_ts].copy()

if df.empty:
    st.warning("No match data available at this timeline position.")
    st.stop()

selected_map_name = str(df["map_id"].iloc[0])

if selected_map_name not in MAP_CONFIG:
    st.error(f"Map config not found for {selected_map_name}")
    st.stop()

img_path = MAP_CONFIG[selected_map_name]["image"]

if not img_path.exists():
    st.error(f"Minimap image not found: {img_path}")
    st.stop()

try:
    img = plt.imread(img_path)
except Exception as e:
    st.error(f"Failed to load minimap image: {e}")
    st.stop()

with st.expander("Preview minimap image"):
    st.image(str(img_path), caption=f"{selected_map_name} minimap", use_container_width=True)

# --------------------------------------------------
# TOP METRICS
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Map", selected_map_name)
col2.metric("Player Files", df["user_id"].nunique())
col3.metric("Humans", df[df["user_type"] == "Human"]["user_id"].nunique())
col4.metric("Bots", df[df["user_type"] == "Bot"]["user_id"].nunique())

# --------------------------------------------------
# PREP DATA
# --------------------------------------------------
movement = df[df["event"].isin(["Position", "BotPosition"])].copy()
movement = world_to_map(movement, selected_map_name)

events = df[df["event"].isin([
    "Kill", "Killed",
    "BotKill", "BotKilled",
    "Loot", "KilledByStorm"
])].copy()
events = world_to_map(events, selected_map_name)

# --------------------------------------------------
# VISUALIZATION GUIDE
# --------------------------------------------------
st.subheader("🎨 Visualization Guide")

legend_data = pd.DataFrame({
    "Element": [
        "Human Path",
        "Bot Path",
        "Kill Event",
        "Death Event",
        "Loot Event",
        "Storm Death",
        "Traffic Heatmap",
        "Kill Zone Heatmap",
        "Death Zone Heatmap"
    ],
    "Style / Color": [
        "Green solid line",
        "Blue dashed line",
        "Red circle",
        "Black X",
        "Yellow circle",
        "Purple star",
        "Cool (blue) → warm (red)",
        "Black → red → orange → white",
        "Black → purple → orange → white"
    ],
    "Meaning": [
        "Movement of human players",
        "Movement of bots",
        "Where a kill happened",
        "Where a death happened",
        "Where loot was picked up",
        "Where a player died to storm",
        "Low to high player traffic",
        "Low to high kill density",
        "Low to high death density"
    ]
})
st.table(legend_data)

# --------------------------------------------------
# EVENT COUNTS
# --------------------------------------------------
kill_count = len(events[events["event"].isin(["Kill", "BotKill"])])
death_count = len(events[events["event"].isin(["Killed", "BotKilled"])])
loot_count = len(events[events["event"] == "Loot"])
storm_count = len(events[events["event"] == "KilledByStorm"])

st.subheader("📊 Event Counts")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Kills", kill_count)
c2.metric("Deaths", death_count)
c3.metric("Loot", loot_count)
c4.metric("Storm Deaths", storm_count)

# --------------------------------------------------
# MATCH VISUALIZATION
# --------------------------------------------------
st.subheader("🗺️ Match Visualization")

fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(img, extent=[0, 1024, 1024, 0])

human_plotted = False
bot_plotted = False

for player_id in movement["user_id"].unique():
    player_data = movement[movement["user_id"] == player_id].sort_values("ts")

    if "-" in str(player_id):
        if not human_plotted:
            ax.plot(
                player_data["px"],
                player_data["py"],
                color="green",
                linewidth=1,
                alpha=0.8,
                label="Human Path",
            )
            human_plotted = True
        else:
            ax.plot(
                player_data["px"],
                player_data["py"],
                color="green",
                linewidth=1,
                alpha=0.8,
            )
    else:
        if not bot_plotted:
            ax.plot(
                player_data["px"],
                player_data["py"],
                color="blue",
                linestyle="dashed",
                linewidth=1,
                alpha=0.7,
                label="Bot Path",
            )
            bot_plotted = True
        else:
            ax.plot(
                player_data["px"],
                player_data["py"],
                color="blue",
                linestyle="dashed",
                linewidth=1,
                alpha=0.7,
            )

if show_kills:
    kill_events = events[events["event"].isin(["Kill", "BotKill"])]
    if not kill_events.empty:
        ax.scatter(
            kill_events["px"],
            kill_events["py"],
            color="red",
            s=90,
            marker="o",
            edgecolors="white",
            linewidths=0.8,
            label="Kill",
            zorder=5
        )

if show_deaths:
    death_events = events[events["event"].isin(["Killed", "BotKilled"])]
    if not death_events.empty:
        ax.scatter(
            death_events["px"],
            death_events["py"],
            color="black",
            s=110,
            marker="x",
            linewidths=2,
            label="Death",
            zorder=6
        )

if show_loot:
    loot_events = events[events["event"] == "Loot"]
    if not loot_events.empty:
        ax.scatter(
            loot_events["px"],
            loot_events["py"],
            color="yellow",
            s=55,
            marker="o",
            edgecolors="black",
            linewidths=0.6,
            label="Loot",
            zorder=4
        )

if show_storm:
    storm_events = events[events["event"] == "KilledByStorm"]
    if not storm_events.empty:
        ax.scatter(
            storm_events["px"],
            storm_events["py"],
            color="purple",
            s=180,
            marker="*",
            edgecolors="white",
            linewidths=0.8,
            label="Storm Death",
            zorder=7
        )

ax.set_xlim(0, 1024)
ax.set_ylim(1024, 0)
ax.set_title(f"Match: {selected_match}")
ax.axis("off")

handles, labels = ax.get_legend_handles_labels()
if handles:
    ax.legend(loc="upper right", fontsize=8)

st.pyplot(fig, use_container_width=True)

# --------------------------------------------------
# HEATMAPS (TABS)
# --------------------------------------------------
if show_heatmap:
    st.subheader("🔥 Heatmaps")

    kill_heat = events[events["event"].isin(["Kill", "BotKill"])].copy()
    death_heat = events[events["event"].isin(["Killed", "BotKilled", "KilledByStorm"])].copy()

    tab1, tab2, tab3 = st.tabs(["Traffic", "Kill Zones", "Death Zones"])

    with tab1:
        st.caption("Side color bar = player density. Cooler colors mean lower activity; warmer colors mean higher activity.")

        fig2, ax2 = plt.subplots(figsize=(8, 8))
        ax2.imshow(img, extent=[0, 1024, 1024, 0])

        if not movement.empty:
            hb = ax2.hexbin(
                movement["px"],
                movement["py"],
                gridsize=60,
                cmap="jet",
                alpha=0.45,
                mincnt=2,
                linewidths=0
            )
            cbar = fig2.colorbar(hb, ax=ax2, fraction=0.035, pad=0.02)
            cbar.set_label("Player Traffic Density")

        ax2.set_xlim(0, 1024)
        ax2.set_ylim(1024, 0)
        ax2.set_title("Player Movement / Traffic Heatmap")
        ax2.axis("off")

        st.pyplot(fig2, use_container_width=True)

    with tab2:
        st.caption("Side color bar = kill density. Brighter colors indicate stronger combat concentration.")

        fig3, ax3 = plt.subplots(figsize=(8, 8))
        ax3.imshow(img, extent=[0, 1024, 1024, 0])

        if not kill_heat.empty:
            hb2 = ax3.hexbin(
                kill_heat["px"],
                kill_heat["py"],
                gridsize=22,
                cmap="hot",
                alpha=0.75,
                mincnt=1,
                linewidths=0
            )
            cbar2 = fig3.colorbar(hb2, ax=ax3, fraction=0.035, pad=0.02)
            cbar2.set_label("Kill Density")
        else:
            ax3.text(
                512, 512,
                "No kill events in current selection",
                ha="center", va="center",
                fontsize=12, color="white",
                bbox=dict(facecolor="black", alpha=0.6)
            )

        ax3.set_xlim(0, 1024)
        ax3.set_ylim(1024, 0)
        ax3.set_title("Kill Zone Heatmap")
        ax3.axis("off")

        st.pyplot(fig3, use_container_width=True)

    with tab3:
        st.caption("Side color bar = death density. Brighter areas indicate where deaths are concentrated.")

        fig4, ax4 = plt.subplots(figsize=(8, 8))
        ax4.imshow(img, extent=[0, 1024, 1024, 0])

        if not death_heat.empty:
            hb3 = ax4.hexbin(
                death_heat["px"],
                death_heat["py"],
                gridsize=22,
                cmap="magma",
                alpha=0.75,
                mincnt=1,
                linewidths=0
            )
            cbar3 = fig4.colorbar(hb3, ax=ax4, fraction=0.035, pad=0.02)
            cbar3.set_label("Death Density")
        else:
            ax4.text(
                512, 512,
                "No death events in current selection",
                ha="center", va="center",
                fontsize=12, color="white",
                bbox=dict(facecolor="black", alpha=0.6)
            )

        ax4.set_xlim(0, 1024)
        ax4.set_ylim(1024, 0)
        ax4.set_title("Death Zone Heatmap")
        ax4.axis("off")

        st.pyplot(fig4, use_container_width=True)

# --------------------------------------------------
# TABLES
# --------------------------------------------------
with st.expander("View Match Summary Table"):
    st.dataframe(
        filtered_summary[[
            "match_id", "map_id", "player_files",
            "kills", "deaths", "storm_deaths", "combat_score"
        ]],
        use_container_width=True
    )

with st.expander("View Raw Event Data"):
    st.dataframe(df.head(200), use_container_width=True)