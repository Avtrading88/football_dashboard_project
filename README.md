# European Football Analytics Dashboard

A modern Streamlit dashboard for exploring European football player statistics for the 2025/2026 season.

The dashboard includes filters, KPI cards, player tables, league comparisons, goal and assist charts, card statistics, goalkeeper analysis, player similarity search, clustering, radar comparison, scouting scores, young talent detection, league analysis, player profile mapping, predictive models, and advanced football metrics.

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
    ├── pages.py
    ├── light_pages.py
    ├── player_similarity.py
    ├── player_clustering.py
    ├── player_radar.py
    ├── player_scouting.py
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
| `src/pages.py`              | Contains the dashboard pages for dark mode.                                             |
| `src/light_pages.py`        | Contains the dashboard pages for light mode.                                            |
| `src/player_similarity.py`  | Creates the player similarity feature using standardized metrics and cosine similarity. |
| `src/player_clustering.py`  | Groups players into similar performance profiles using KMeans clustering.               |
| `src/player_radar.py`       | Creates radar chart data for comparing multiple players.                                |
| `src/player_scouting.py`    | Calculates custom player scores and young talent scores.                                |
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
* Young talent detection
* Advanced league comparison analysis
* Player profile map using PCA
* Predictive model for player goals
* Predictive classifier for top performers
* Advanced football metrics including xG efficiency, xAG analysis, per-90 metrics, progressive actions, and discipline risk
* Cleaner numeric formatting, so whole numbers show as integers instead of values like `25.000000`

## Machine Learning and Analytics Features

### Player Similarity Finder

The player similarity feature allows users to select one player and find statistically similar players based on selected metrics. It uses standardized numerical features and cosine similarity.

### Player Clustering

The clustering feature groups players into similar performance profiles using KMeans clustering. The dashboard also gives each cluster a more understandable profile name and description.

### Radar Chart Comparison

The radar chart allows users to compare multiple players across selected statistics. Metrics are normalized from 0 to 100 so that different types of statistics can be compared in one visual.

### Player Scoring System

The player scoring system creates a custom score from 0 to 100 based on goals, assists, expected output, and progressive actions. Users can adjust the weights to change what matters most.

### Young Talent Detection

The young talent feature ranks young players based on performance, age, and playing time. It is designed to highlight promising players who already show strong output.

### Player Profile Map

The player profile map uses PCA to reduce multiple football statistics into two visual dimensions. Players close to each other on the map have similar statistical profiles.

### Predictive Models

The dashboard includes two exploratory machine learning models:

1. **Goal Prediction Model**
   Predicts player goals using available player statistics.

2. **Top Performer Classifier**
   Predicts whether a player belongs to the top performer group based on attacking output.

### Advanced Football Metrics

The advanced metrics section includes:

* Goals minus expected goals
* Goal efficiency ratio
* Assists minus expected assisted goals
* Goals per 90
* Assists per 90
* Goals + assists per 90
* Expected goals per 90
* Expected assisted goals per 90
* Expected goals + expected assists per 90
* Progressive carries per 90
* Progressive passes per 90
* Total progressive actions
* Discipline risk

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
