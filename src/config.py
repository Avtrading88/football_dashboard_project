from pathlib import Path


# Resolve the dataset independently of the directory used to start Streamlit.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "players_data_light-2025_2026.csv"

# Main colors.
APP_BG = "#020817"
APP_BG_2 = "#06111F"
TEXT_LIGHT = "#F8FAFC"
TEXT_MUTED = "#93A4B8"
GRID_COLOR = "#1E293B"

NEON = "#B7FF3C"
BLUE = "#38BDF8"
TEAL = "#14B8A6"
RED = "#EF4444"
YELLOW = "#FACC15"
CYAN = "#22D3EE"

# Chart palette.
COLOR_PALETTE = [
    "#B7FF3C",
    "#38BDF8",
    "#14B8A6",
    "#8B5CF6",
    "#F59E0B",
    "#EF4444",
    "#FACC15",
    "#22D3EE",
    "#EC4899",
    "#6366F1",
]
