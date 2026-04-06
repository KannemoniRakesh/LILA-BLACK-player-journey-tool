 Architecture – Player Journey Visualization Tool
________________________________________
📌 Overview
The Player Journey Visualization Tool is designed to process raw gameplay logs and convert them into meaningful visual insights.
The architecture follows a simple and efficient pipeline:
Parquet Files → Pandas Processing → Coordinate Mapping → Visualization → UI (Streamlit)
________________________________________
🧩 System Components
1. 📂 Data Layer
•	Source: Player telemetry stored as Parquet files
•	Each file represents:
o	Player movement
o	Events (kill, death, loot, storm)
•	Organized by:
•	Data/player_data/<date>/<match_files>
________________________________________
2. ⚙️ Data Processing Layer
Handled using Pandas + PyArrow
Key responsibilities:
•	Load multiple parquet files per match
•	Merge into a single DataFrame
•	Decode event types
•	Classify players:
o	Humans → UUID format
o	Bots → Numeric IDs
df["user_type"] = df["user_id"].apply(lambda x: "Bot" if is_bot(x) else "Human")
________________________________________
3. 🗺️ Coordinate Mapping System
Game world coordinates (x, z) are transformed into minimap pixel coordinates.
Formula:
u = (x - origin_x) / scale
v = (z - origin_z) / scale

px = u * map_width
py = (1 - v) * map_height
Why this matters:
•	Aligns gameplay data with minimap images
•	Enables accurate spatial visualization
Each map has its own config:
MAP_CONFIG = {
  "AmbroseValley": {scale, origin_x, origin_z},
  ...
}
________________________________________
4. 📊 Visualization Layer
Built using Matplotlib
Components:
a. Player Paths
•	Humans → Green solid lines
•	Bots → Blue dashed lines
b. Event Markers
•	Kill → Red circles
•	Death → Black X
•	Loot → Yellow
•	Storm → Purple star
________________________________________
5. 🔥 Heatmap Engine
Implemented using hexbin plots
Types:
Heatmap	Purpose
Traffic	Player movement density
Kill Zone	Combat hotspots
Death Zone	Death concentration
Example:
ax.hexbin(x, y, gridsize=60, cmap="jet")
Design choice:
•	Hexbin → better density representation than scatter
•	Color intensity → reflects frequency
________________________________________
6. ⏱️ Timeline Engine
Enables time-based filtering
Logic:
current_ts = min_ts + (max_ts - min_ts) * (slider_value / 100)
df = df[df["ts"] <= current_ts]
Outcome:
•	Simulates match progression
•	Helps understand when events occur
________________________________________
7. 🎛️ UI Layer (Streamlit)
Streamlit acts as:
•	UI framework
•	State manager
•	Rendering engine
Key elements:
•	Sidebar filters
•	Interactive sliders
•	Toggle controls
•	Dynamic plots
________________________________________
🔄 Data Flow
User selects filters
        ↓
Load match data
        ↓
Filter by timeline
        ↓
Transform coordinates
        ↓
Render:
   → Paths
   → Events
   → Heatmaps
________________________________________
⚖️ Design Decisions
✅ Why Streamlit?
•	Fast prototyping
•	Built-in interactivity
•	Minimal frontend overhead
✅ Why Parquet?
•	Efficient storage
•	Faster read vs CSV
•	Suitable for large datasets
✅ Why Matplotlib?
•	Full control over visualization
•	Works well with static map overlays
________________________________________
🚧 Limitations
•	No real-time data streaming
•	Static minimap images (no zoom/pan)
•	Limited animation (slider-based only)
•	No clustering or ML-based insights
________________________________________
🚀 Scalability Considerations
To scale further:
•	Use DuckDB / Spark for large datasets
•	Add caching layer for repeated queries
•	Move to Plotly/WebGL for smoother rendering
•	Introduce backend API layer
________________________________________
🧠 Key Takeaway
The architecture prioritizes:
•	Simplicity
•	Speed
•	Interpretability
While remaining flexible enough to scale into a production-grade analytics system.
________________________________________

