# European Football Analytics Dashboard

A dark, modern Streamlit dashboard for exploring European football player statistics for the 2025/2026 season.

The dashboard includes filters, KPI cards, player tables, league comparisons, goal and assist charts, card statistics, and goalkeeper analysis.

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
    ├── data_loader.py
    ├── components.py
    ├── charts.py
    ├── filters.py
    └── pages.py
```

## What Each File Does

| File | Purpose |
|---|---|
| `app.py` | Starts the Streamlit app and controls the main page flow. |
| `src/config.py` | Stores the CSV path, colors, and chart palette. |
| `src/styles.py` | Contains the custom CSS design. |
| `src/data_loader.py` | Loads, renames, cleans, and formats the CSV data. |
| `src/components.py` | Contains reusable UI parts like KPI cards and styled tables. |
| `src/charts.py` | Contains reusable Plotly chart functions. |
| `src/filters.py` | Builds all sidebar filters. |
| `src/pages.py` | Contains the dashboard pages: Overview, Competitions, Players, and Goalkeepers. |
| `data/` | Stores the CSV dataset. |

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

- Dark neon dashboard design
- Sidebar filters for league, club, position, nationality, age, matches, goals, assists, and player name
- KPI cards for players, goals, assists, and average age
- Top scorers and top assist players
- Goals and assists by league
- Players by position
- Cards by club
- League comparison page
- Player data page
- Goalkeeper analysis page
- Cleaner numeric formatting, so whole numbers show as integers instead of values like `25.000000`

## Notes

If Streamlit cannot find the CSV file, check that the folder name and file name match exactly:

```text
data/players_data_light-2025_2026.csv
```

If you change the CSV filename, update `DATA_PATH` inside `src/config.py`.
