# European Football Analytics Dashboard

A modern Streamlit dashboard for exploring European football player statistics for the 2025/2026 season.

The dashboard includes filters, KPI cards, player tables, league comparisons, goal and assist charts, shooting and defensive analysis, goalkeeper analysis, transfer-safe player selection, similarity search, clustering, radar comparison, role-specific scouting scores, young talent detection, a persistent recruitment shortlist, CSV/PDF scouting exports, player profile mapping, predictive models, and advanced football metrics.

## Project Structure

```text
football_dashboard_project/
│
├── app.py
├── README.md
├── requirements.txt
│
├── data/
│   └── players_data_light-2025_2026.csv
│
└── src/
    ├── __init__.py
    ├── config.py
    ├── styles.py
    ├── light_config.py
    ├── light_styles.py
    ├── data_loader.py
    ├── components.py
    ├── light_components.py
    ├── charts.py
    ├── light_charts.py
    ├── filters.py
    ├── feature_engineering.py
    ├── pages.py
    ├── light_pages.py
    ├── player_similarity.py
    ├── player_clustering.py
    ├── player_radar.py
    ├── player_scouting.py
    ├── shortlist_store.py
    ├── shortlist_ui.py
    ├── scouting_exports.py
    ├── league_analysis.py
    ├── player_pca.py
    └── player_predictions.py
```

## Data Source

The dataset used in this project comes from Kaggle:

**Football Players Stats (2025–2026)**
Link: https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2025-2026

The dataset contains football player statistics for the 2025–2026 season from the top five European leagues. According to the Kaggle dataset description, the original statistics are sourced from FBref.

This project uses the dataset for educational and portfolio purposes.

### Data coverage and limitations

The included snapshot contains 2,839 player-club rows and 53 source columns. It contains shooting, defensive, discipline, and goalkeeper statistics, but it does **not** contain xG, xAG, or progressive-action columns. The application therefore shows xG/progression features only when a future dataset actually provides those fields.

Players who represented multiple clubs remain separate player-club records. A derived player ID groups those records for correct unique-player counts, while a separate record ID keeps transfer rows selectable in similarity and radar tools.

## What Each File Does

| File                        | Purpose                                                                                 |
| --------------------------- | --------------------------------------------------------------------------------------- |
| `app.py`                    | Starts the Streamlit app, controls theme selection, navigation, and page flow.          |
| `src/config.py`             | Stores the CSV path, dark theme colors, and chart palette.                              |
| `src/light_config.py`       | Stores the light theme colors and chart palette.                                        |
| `src/styles.py`             | Contains the custom CSS design for dark mode.                                           |
| `src/light_styles.py`       | Contains the custom CSS design for light mode.                                          |
| `src/data_loader.py`        | Loads, renames, cleans, and formats the CSV data.                                       |
| `src/components.py`         | Contains reusable dark-mode UI parts like KPI cards and styled tables.                  |
| `src/light_components.py`   | Contains reusable light-mode UI parts like KPI cards and styled tables.                 |
| `src/charts.py`             | Contains reusable Plotly chart functions for dark mode.                                 |
| `src/light_charts.py`       | Contains reusable Plotly chart functions for light mode.                                |
| `src/filters.py`            | Builds all sidebar filters.                                                             |
| `src/feature_engineering.py`| Creates stable player identities and shared per-90, shooting, defensive, and goalkeeper metrics. |
| `src/pages.py`              | Contains the dashboard pages for dark mode.                                             |
| `src/light_pages.py`        | Contains the dashboard pages for light mode.                                            |
| `src/player_similarity.py`  | Creates the player similarity feature using standardized metrics and cosine similarity. |
| `src/player_clustering.py`  | Groups players into similar performance profiles using KMeans clustering.               |
| `src/player_radar.py`       | Creates radar chart data for comparing multiple players.                                |
| `src/player_scouting.py`    | Calculates custom player scores and young talent scores.                                |
| `src/shortlist_store.py`    | Persists transfer candidates, statuses, priorities, target fees, ratings, and notes in local SQLite. |
| `src/shortlist_ui.py`       | Provides quick-add actions and the complete recruitment workspace in both themes.       |
| `src/scouting_exports.py`   | Builds Excel-friendly shortlist CSV files and professional PDF scouting reports.         |
| `src/league_analysis.py`    | Creates advanced league comparison summaries.                                           |
| `src/player_pca.py`         | Creates the player profile map using PCA.                                               |
| `src/player_predictions.py` | Builds predictive models and advanced football metrics.                                 |
| `data/`                     | Stores the CSV dataset.                                                                 |

## Dataset Path

The app expects the CSV file here:

```text
data/players_data_light-2025_2026.csv
```

This path is set in:

```python
src/config.py
```

```python
DATA_PATH = "data/players_data_light-2025_2026.csv"
```

## Installation

Create and activate a virtual environment.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Run the Dashboard

From the main project folder, run:

```bash
streamlit run app.py
```

Then open the local Streamlit link in your browser.

## Features

* Dark and light dashboard themes
* Sidebar filters for league, club, position, nationality, age, matches, goals, assists, and player name
* KPI cards for players, goals, assists, and average age
* Top scorers and top assist players
* Shooting-performance and defensive-contribution analysis
* Goals and assists by league
* Players by position
* Cards by club
* League comparison page
* Player data page
* Goalkeeper analysis page
* Player similarity finder
* Player clustering with understandable cluster profiles
* Radar chart for player comparison
* Custom player scoring system
* Position-relative scouting scores for forwards, midfielders, defenders, and goalkeepers
* Young talent detection
* Persistent transfer shortlist with recruitment statuses and priorities
* Scout notes, target fees, ratings, candidate editing, and removal
* Side-by-side shortlist comparison with normalized radar analytics
* CSV shortlist export and multi-player PDF scouting reports
* Advanced league comparison analysis
* Player profile map using PCA
* Predictive model for player goals
* Predictive classifier for top performers
* Advanced shooting, defensive, discipline, goalkeeper, and per-90 metrics
* Optional xG and progression analytics when those columns are available
* Cleaner numeric formatting, so whole numbers show as integers instead of values like `25.000000`

## Machine Learning and Analytics Features

### Player Similarity Finder

The player similarity feature allows users to select one player and find statistically similar players based on selected metrics. It uses standardized numerical features and cosine similarity.

### Player Clustering

The clustering feature groups players into similar performance profiles using KMeans clustering. The dashboard also gives each cluster a more understandable profile name and description.

### Radar Chart Comparison

The radar chart allows users to compare multiple players across selected statistics. Metrics are normalized from 0 to 100 so that different types of statistics can be compared in one visual.

### Player Scoring System

The custom player scoring system creates a score from 0 to 100 and rebalances its denominator when optional metrics are unavailable instead of silently treating missing data as zero. The role-specific score compares players only with positional peers and uses different profiles for forwards, midfielders, defenders, and goalkeepers.

### Young Talent Detection

The young talent feature ranks young players based on performance, age, and playing time. It is designed to highlight promising players who already show strong output.

### Transfer Shortlist and Recruitment Workspace

Players can be saved from the Players, Player Similarity, Scouting, or Transfer Shortlist pages. Saved candidates remain available after the app restarts in `data/transfer_shortlist.sqlite3`. The local database is excluded from Git so personal scout notes and recruitment decisions are not published accidentally.

Each candidate supports the workflow statuses Watching, Scouted, Priority, Contacted, and Rejected. Recruitment staff can also assign Low, Medium, High, or Critical priority, record a target fee, add a 0-100 scout rating, keep notes, compare two to five candidates, and export selected entries as CSV or PDF.

The SQLite storage is designed for local and single-user portfolio use. A future hosted multi-user deployment should move shortlist storage to a managed database with authentication and role-based access.

### Player Profile Map

The player profile map uses PCA to reduce multiple football statistics into two visual dimensions. Players close to each other on the map have similar statistical profiles.

### Predictive Models

The dashboard includes two exploratory machine learning models:

1. **Goal Prediction Model**
   Predicts player goals using available player statistics.

2. **Top Performer Classifier**
   Predicts whether a player belongs to the top performer group based on attacking output.

### Advanced Football Metrics

The advanced metrics section includes the metrics actually supported by the bundled snapshot:

* Goals per 90
* Non-penalty goals per 90
* Assists per 90
* Goals + assists per 90
* Shots and shots on target per 90
* Shooting accuracy and goal conversion
* Crosses per 90
* Tackles won, interceptions, and defensive actions per 90
* Fouls committed and received per 90
* Save, clean-sheet, and penalty-save percentages
* Discipline risk

If xG, xAG, or progression columns are supplied later, their derived metrics and charts are enabled automatically.

## Disclaimer

This dashboard is a portfolio and educational football analytics project. The predictive models are exploratory and trained on the available season data. They are intended to demonstrate machine learning workflow and interactive football analytics, not to provide professional betting or scouting predictions.

The results should be interpreted as analytical insights, not as professional scouting, transfer, or betting advice.

## Notes

If Streamlit cannot find the CSV file, check that the folder name and file name match exactly:

```text
data/players_data_light-2025_2026.csv
```

If you change the CSV filename, update `DATA_PATH` inside `src/config.py`.

## Technologies Used

* Python
* Streamlit
* Pandas
* Plotly
* Scikit-learn
* NumPy

## Author

Vladimir Trifonov
