import streamlit as st

from src.styles import apply_styles
from src.data_loader import load_data
from src.filters import apply_sidebar_filters
from src.components import kpi_card
from src.pages import (
    show_overview_page,
    show_competitions_page,
    show_players_page,
    show_goalkeepers_page,
)

# Page settings.
st.set_page_config(
    page_title="European Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide"
)

# Load custom design.
apply_styles()

# Load player data.
players_df = load_data()

# Apply sidebar filters.
filtered_df = apply_sidebar_filters(players_df)

# Stop if filters return no rows.
if filtered_df.empty:
    st.warning("No data found for your filters.")
    st.stop()

# Main title area.
st.markdown(
    """
    <div class="dashboard-hero">
        <div class="dashboard-badge">⚽ Football Analytics Dashboard</div>
        <div class="dashboard-title">European Football <span>Player Insights</span></div>
        <div class="dashboard-subtitle">
            Explore players, competitions, positions, cards, assists, goals and goalkeeper performance 
            in the top five European competitions.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# KPI values.
players_count = filtered_df["Player Name"].nunique()
goals_total = int(filtered_df["Goals"].sum()) if "Goals" in filtered_df.columns else 0
assists_total = int(filtered_df["Assists"].sum()) if "Assists" in filtered_df.columns else 0
avg_age = round(filtered_df["Age"].mean(), 1) if "Age" in filtered_df.columns else 0

# KPI cards.
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Players", f"{players_count:,}", "filtered players")
with k2:
    kpi_card("Goals", f"{goals_total:,}", "total goals")
with k3:
    kpi_card("Assists", f"{assists_total:,}", "total assists")
with k4:
    kpi_card("Average Age", f"{avg_age}", "filtered average")

# Top navigation.
page = st.radio(
    "Navigation",
    ["Overview", "Competitions", "Players", "Goalkeepers"],
    horizontal=True,
    label_visibility="collapsed",
)

# Show selected page.
if page == "Overview":
    show_overview_page(filtered_df)
elif page == "Competitions":
    show_competitions_page(filtered_df)
elif page == "Players":
    show_players_page(filtered_df)
elif page == "Goalkeepers":
    show_goalkeepers_page(filtered_df)
