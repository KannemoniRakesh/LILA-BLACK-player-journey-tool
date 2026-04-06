🎮 LILA BLACK – Player Journey Visualization Tool
🚀 Live App:
https://lila-black-player-journey-tool-extbwetykr47sfpgr5gufh.streamlit.app/
________________________________________
📌 Overview
The Player Journey Visualization Tool is an interactive analytics dashboard designed to help game designers understand player behaviour across matches.
It visualizes:
•	Player movement paths (humans vs bots)
•	Combat hotspots (kills & deaths)
•	Loot interactions
•	Storm-related eliminations
•	Match progression over time
The tool enables data-driven level design decisions by identifying high-traffic zones, combat areas, and player behaviour patterns.
________________________________________
✨ Key Features
🗺️ Match Visualization
•	Human paths → Green solid lines
•	Bot paths → Blue dashed lines
•	Kill markers → Red circles
•	Death markers → Black X
•	Loot → Yellow circles
•	Storm deaths → Purple stars
________________________________________
⏱️ Timeline Playback
•	Replay match progression using a slider
•	Understand how engagements evolve over time
________________________________________
🔥 Heatmaps
•	Traffic Heatmap → Player movement density
•	Kill Zone Heatmap → Combat hotspots
•	Death Zone Heatmap → Death concentration areas
________________________________________
🎛️ Interactive Filters
•	Filter by:
o	Date
o	Map
o	Match
o	Minimum player count
•	Toggle visibility of events (kills, loot, etc.)
________________________________________
🧠 Why This Tool Matters
This tool helps answer critical design questions:
•	Where do players fight the most?
•	Are loot locations influencing combat?
•	Do bots behave differently from humans?
•	Where do players die frequently (design flaws?)
________________________________________
🏗️ Tech Stack
•	Frontend / App: Streamlit
•	Data Processing: Pandas
•	File Format: Parquet (PyArrow)
•	Visualization: Matplotlib
•	Deployment: Streamlit Cloud
________________________________________
📂 Project Structure
LILA-BLACK-player-journey-tool/
│
├── app.py
├── requirements.txt
├── README.md
├── Data/
│   └── player_data/
│       ├── February_10/
│       └── minimaps/
________________________________________
⚙️ How to Run Locally
1. Clone the repo
git clone https://github.com/KannemoniRakesh/LILA-BLACK-player-journey-tool.git
cd LILA-BLACK-player-journey-tool
2. Install dependencies
pip install -r requirements.txt
3. Run the app
streamlit run app.py
________________________________________
📊 Data Note
⚠️ Due to GitHub file size limitations, only a sample dataset is included.
The tool is designed to scale and works with:
•	Large match datasets
•	Multiple days of gameplay logs
________________________________________
🧩 Key Components
•	Match Loader → Reads parquet files per match
•	Event Parser → Extracts kills, deaths, loot, etc.
•	Coordinate Mapper → Converts world coordinates → minimap
•	Visualizer → Renders paths, markers, heatmaps
•	Timeline Engine → Filters events by timestamp
________________________________________
🚀 Future Improvements
•	Animated playback instead of slider
•	Team-level analytics
•	Weapon usage insights
•	Zone shrinking visualization (storm circles)
•	Player clustering detection
________________________________________
🙌 Author
Kannemoni Rakesh
Specialist → Aspiring Product Manager
________________________________________
📎 Submission
This project demonstrates:
•	Product thinking
•	Data interpretation
•	Visualization design
•	End-to-end execution (data → insight → UI)


