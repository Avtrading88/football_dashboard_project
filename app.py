import streamlit as st

from src.data_loader import load_data
from src.filters import apply_sidebar_filters

# Page settings.
st.set_page_config(
    page_title="European Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide"
)

# Theme selector: the whole dashboard now runs from this one app.py file.
theme = st.sidebar.radio(
    "Dashboard theme",
    ["Dark Mode", "Light Mode"],
    horizontal=True,
)

if theme == "Light Mode":
    from src.light_styles import apply_light_styles as apply_dashboard_styles
    from src.light_components import kpi_card
    from src.light_pages import (
        show_overview_page,
        show_competitions_page,
        show_players_page,
        show_goalkeepers_page,
        show_similarity_page,
        show_clustering_page,
        show_radar_page,
        show_scouting_page,
        show_transfer_shortlist_page,
        show_league_analysis_page,
        show_pca_page,
        show_predictions_page,
    )
else:
    from src.styles import apply_styles as apply_dashboard_styles
    from src.components import kpi_card
    from src.pages import (
        show_overview_page,
        show_competitions_page,
        show_players_page,
        show_goalkeepers_page,
        show_similarity_page,
        show_clustering_page,
        show_radar_page,
        show_scouting_page,
        show_transfer_shortlist_page,
        show_league_analysis_page,
        show_pca_page,
        show_predictions_page,
    )

# Load the selected design.
apply_dashboard_styles()

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
            Take a look at the top five European Leagues and see how players perform in terms of positions,
            cards, assists, goals and goalkeeper performance.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# KPI values.
player_identity_column = (
    "Player ID" if "Player ID" in filtered_df.columns else "Player Name"
)
players_count = filtered_df[player_identity_column].nunique()
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
    [
        "Overview",
        "Competitions",
        "Players",
        "Goalkeepers",
        "Player Similarity",
        "Player Clustering",
        "Player Radar",
        "Scouting",
        "Transfer Shortlist",
        "League Analysis",
        "Player Profile Map",
        "Predictions & Metrics"
    ],
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
elif page == "Player Similarity":
    show_similarity_page(filtered_df)
elif page == "Player Clustering":
    show_clustering_page(filtered_df)
elif page == "Player Radar":
    show_radar_page(filtered_df)
elif page == "Scouting":
    show_scouting_page(filtered_df)
elif page == "Transfer Shortlist":
    show_transfer_shortlist_page(players_df)
elif page == "League Analysis":
    show_league_analysis_page(filtered_df)
elif page == "Player Profile Map":
    show_pca_page(filtered_df)
elif page == "Predictions & Metrics":
    show_predictions_page(filtered_df)
