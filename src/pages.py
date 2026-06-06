import streamlit as st
import plotly.graph_objects as go

from src.components import centered_dataframe
from src.charts import make_horizontal_bar, chart_layout
from src.config import APP_BG, TEXT_LIGHT, GRID_COLOR, TEAL, BLUE, NEON, YELLOW, RED


def show_overview_page(filtered_df):
    """Show the main dashboard page."""
    players_count = filtered_df["Player Name"].nunique()
    goals_total = int(filtered_df["Goals"].sum()) if "Goals" in filtered_df.columns else 0

    space_left, col1, gap, col2, space_right = st.columns([0.08, 1, 0.04, 1, 0.08])

    with col1:
        st.subheader("Top 10 Scoring Players")
        top_scorers = (
            filtered_df.groupby("Player Name", as_index=False)
            .agg({"Goals": "sum", "Assists": "sum", "Matches Played": "sum"})
            .sort_values("Goals", ascending=False)
            .head(10)
        )
        centered_dataframe(top_scorers)
        fig = make_horizontal_bar(
            data=top_scorers,
            x_col="Goals",
            y_col="Player Name",
            color_col="Player Name",
            title="Top 10 Scoring Players",
            x_title="Sum of Goals",
            y_title="Player Name",
            height=430,
            show_legend=False,
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Top 10 Assist Players")
        top_assists = (
            filtered_df.groupby("Player Name", as_index=False)
            .agg({"Assists": "sum", "Goals": "sum", "Matches Played": "sum"})
            .sort_values("Assists", ascending=False)
            .head(10)
        )
        centered_dataframe(top_assists)
        fig = make_horizontal_bar(
            data=top_assists,
            x_col="Assists",
            y_col="Player Name",
            color_col="Player Name",
            title="Top 10 Assist Players",
            x_title="Sum of Assists",
            y_title="Player Name",
            height=430,
            show_legend=False,
        )
        st.plotly_chart(fig, width="stretch")

    space_left, col3, gap, col4, space_right = st.columns([0.08, 1, 0.04, 2, 0.08])

    with col3:
        st.subheader("Average Goals per Player")
        avg_goals = round(goals_total / players_count, 1) if players_count > 0 else 0
        gauge_max = max(10, avg_goals + 2)
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=avg_goals,
                number={"font": {"size": 44, "color": TEXT_LIGHT}},
                gauge={
                    "axis": {"range": [0, gauge_max], "tickcolor": TEXT_LIGHT},
                    "bar": {"color": TEAL},
                    "bgcolor": APP_BG,
                    "borderwidth": 1,
                    "bordercolor": GRID_COLOR,
                    "steps": [
                        {"range": [0, gauge_max * 0.25], "color": "#102A43"},
                        {"range": [gauge_max * 0.25, gauge_max * 0.50], "color": "#14532D"},
                        {"range": [gauge_max * 0.50, gauge_max * 0.75], "color": "#6B8E23"},
                        {"range": [gauge_max * 0.75, gauge_max], "color": "#9ACD32"},
                    ],
                },
            )
        )
        gauge.update_layout(
            title="Average Goals",
            paper_bgcolor=APP_BG,
            font=dict(color=TEXT_LIGHT),
            height=390,
            margin=dict(l=20, r=20, t=45, b=20)
        )
        st.plotly_chart(gauge, width="stretch")

    with col4:
        st.subheader("Goals and Assists by League")
        league_trends = (
            filtered_df.groupby("League", as_index=False)
            .agg({"Goals": "sum", "Assists": "sum"})
            .sort_values("Goals", ascending=False)
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(x=league_trends["League"], y=league_trends["Goals"], name="Goals", marker_color=BLUE, text=league_trends["Goals"], textposition="inside"))
        fig.add_trace(go.Bar(x=league_trends["League"], y=league_trends["Assists"], name="Assists", marker_color=NEON, text=league_trends["Assists"], textposition="inside"))
        fig.update_layout(title="Goals and Assists by League", xaxis_title="League", yaxis_title="Total", barmode="stack")
        chart_layout(fig, 390)
        st.plotly_chart(fig, width="stretch")

    space_left, col5, gap, col6, space_right = st.columns([0.08, 1, 0.04, 1, 0.08])

    with col5:
        st.subheader("Players by Position")
        players_by_position = (
            filtered_df.groupby("Position", as_index=False)
            .agg({"Player Name": "nunique"})
            .rename(columns={"Player Name": "Number of Players"})
            .sort_values("Number of Players", ascending=False)
        )
        centered_dataframe(players_by_position)
        fig = make_horizontal_bar(
            data=players_by_position,
            x_col="Number of Players",
            y_col="Position",
            color_col="Position",
            title="Players by Position",
            x_title="Number of Players",
            y_title="Position",
            height=430,
            show_legend=False,
        )
        st.plotly_chart(fig, width="stretch")

    with col6:
        st.subheader("Cards by Club")
        cards_by_club = (
            filtered_df.groupby("Club", as_index=False)
            .agg({"Yellow Cards": "sum", "Red Cards": "sum"})
            .sort_values("Yellow Cards", ascending=False)
            .head(10)
        )
        centered_dataframe(cards_by_club)
        fig = go.Figure()
        fig.add_trace(go.Bar(y=cards_by_club["Club"], x=cards_by_club["Yellow Cards"], name="Yellow Cards", orientation="h", marker_color=YELLOW, text=cards_by_club["Yellow Cards"], textposition="inside"))
        fig.add_trace(go.Bar(y=cards_by_club["Club"], x=cards_by_club["Red Cards"], name="Red Cards", orientation="h", marker_color=RED, text=cards_by_club["Red Cards"], textposition="inside"))
        fig.update_layout(title="Cards by Club", xaxis_title="Cards", yaxis_title="Club", barmode="stack")
        fig.update_yaxes(autorange="reversed")
        chart_layout(fig, 430)
        st.plotly_chart(fig, width="stretch")


def show_competitions_page(filtered_df):
    """Show league comparison charts."""
    st.subheader("Competition Comparison")
    competition_df = (
        filtered_df.groupby("League", as_index=False)
        .agg({
            "Player Name": "nunique",
            "Club": "nunique",
            "Goals": "sum",
            "Assists": "sum",
            "Matches Played": "sum",
            "Age": "mean"
        })
        .rename(columns={
            "Player Name": "Players",
            "Club": "Clubs",
            "Matches Played": "Total Matches Played",
            "Age": "Average Age"
        })
        .sort_values("Goals", ascending=False)
    )
    competition_df["Average Age"] = competition_df["Average Age"].round(1)
    centered_dataframe(competition_df)
    metric = st.selectbox(
        "Choose metric to compare",
        ["Players", "Clubs", "Goals", "Assists", "Total Matches Played", "Average Age"]
    )
    competition_plot = competition_df.sort_values(metric, ascending=False)
    fig = make_horizontal_bar(
        data=competition_plot,
        x_col=metric,
        y_col="League",
        color_col="League",
        title=f"Competition Comparison by {metric}",
        x_title=metric,
        y_title="League",
        height=520,
        show_legend=False,
    )
    st.plotly_chart(fig, width="stretch")


def show_players_page(filtered_df):
    """Show the players table."""
    st.subheader("Player Data")
    default_columns = [
        "Player Name", "Nationality", "Position", "Club", "League",
        "Age", "Matches Played", "Goals", "Assists"
    ]
    default_columns = [col for col in default_columns if col in filtered_df.columns]
    selected_columns = st.multiselect(
        "Choose columns",
        options=list(filtered_df.columns),
        default=default_columns
    )
    if selected_columns:
        centered_dataframe(filtered_df[selected_columns])
    else:
        centered_dataframe(filtered_df)


def show_goalkeepers_page(filtered_df):
    """Show goalkeeper stats only."""
    st.subheader("Goalkeeper Analysis")
    goalkeepers = filtered_df[
        filtered_df["Position"].astype(str).str.contains("GK", case=False, na=False)
    ].copy()
    if goalkeepers.empty:
        st.info("No goalkeepers found for the selected filters.")
        return

    goalkeeper_columns = [
        "Player Name", "Club", "Age", "Matches Played", "Saves",
        "Clean Sheets", "Goals Against", "Goals Against per 90"
    ]
    goalkeeper_columns = [col for col in goalkeeper_columns if col in goalkeepers.columns]
    goalkeepers_table = goalkeepers[goalkeeper_columns].copy()

    if "Saves" in goalkeepers_table.columns:
        goalkeepers_table = goalkeepers_table.sort_values("Saves", ascending=False)

    centered_dataframe(goalkeepers_table)

    if "Saves" in goalkeepers_table.columns:
        goalkeeper_plot = goalkeepers_table.head(10).sort_values("Saves", ascending=False)
        fig = make_horizontal_bar(
            data=goalkeeper_plot,
            x_col="Saves",
            y_col="Player Name",
            color_col="Player Name",
            title="Top Goalkeepers by Saves",
            x_title="Saves",
            y_title="Goalkeeper",
            height=500,
            show_legend=False,
        )
        st.plotly_chart(fig, width="stretch")
