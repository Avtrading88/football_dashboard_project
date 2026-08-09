import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from src.components import centered_dataframe
from src.charts import make_horizontal_bar, chart_layout
from src.config import APP_BG, TEXT_LIGHT, GRID_COLOR, TEAL, BLUE, NEON, YELLOW, RED
from src.player_similarity import (
    find_similar_players,
    prepare_similarity_data,
    get_available_similarity_features,
)

from src.player_clustering import (
    cluster_players,
    get_available_clustering_features,
    describe_cluster_profiles
)

from src.player_radar import (
    create_radar_comparison_data,
    get_available_radar_features,
)

from src.player_scouting import (
    calculate_player_scores,
    calculate_role_percentile_scores,
    calculate_young_talent_scores,
    ROLE_SCORE_PROFILES,
)

from src.league_analysis import (
    create_league_summary,
    create_league_position_summary,
)

from src.player_pca import (
    create_player_pca,
    get_available_pca_features,
)

from src.player_predictions import (
    train_goals_prediction_model,
    train_top_performer_classifier,
    create_advanced_metrics_table,
)
from src.shortlist_ui import (
    render_shortlist_quick_add,
    show_transfer_shortlist_page as show_shared_transfer_shortlist_page,
)


def show_overview_page(filtered_df):
    """Show the main dashboard page."""
    player_identity_column = (
        "Player ID" if "Player ID" in filtered_df.columns else "Player Name"
    )
    players_count = filtered_df[player_identity_column].nunique()
    goals_total = int(filtered_df["Goals"].sum()) if "Goals" in filtered_df.columns else 0

    space_left, col1, gap, col2, space_right = st.columns([0.08, 1, 0.04, 1, 0.08])

    with col1:
        st.subheader("Top 10 Goal Scorers")
        top_scorers = (
            filtered_df.groupby(["Player Name", "Club"], as_index=False)
            .agg({"Goals": "sum", "Assists": "sum", "Matches Played": "sum"})
            .sort_values("Goals", ascending=False)
            .head(10)
        )

        top_scorers["Player"] = (
                top_scorers["Player Name"] + " — " + top_scorers["Club"]
        )

        top_scorers_table = top_scorers[
            ["Player", "Goals", "Assists", "Matches Played"]
        ]

        centered_dataframe(top_scorers_table)

        fig = make_horizontal_bar(
            data=top_scorers,
            x_col="Goals",
            y_col="Player",
            color_col="Player Name",
            title="Top 10 Scoring Players",
            x_title="Sum of Goals",
            y_title="Player / Club",
            height=430,
            show_legend=False,
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Top 10 Assist Players")
        top_assists = (
            filtered_df.groupby(["Player Name", "Club"], as_index=False)
            .agg({"Assists": "sum", "Goals": "sum", "Matches Played": "sum"})
            .sort_values("Assists", ascending=False)
            .head(10)
        )

        top_assists["Player"] = (
                top_assists["Player Name"] + " — " + top_assists["Club"]
        )

        top_assists_table = top_assists[
            ["Player", "Assists", "Goals", "Matches Played"]
        ]

        centered_dataframe(top_assists_table)

        fig = make_horizontal_bar(
            data=top_assists,
            x_col="Assists",
            y_col="Player",
            color_col="Player Name",
            title="Top 10 Assist Players",
            x_title="Sum of Assists",
            y_title="Player / Club",
            height=430,
            show_legend=False,
        )

        st.plotly_chart(fig, width="stretch")

    space_left, col3, gap, col4, space_right = st.columns([0.08, 1, 0.04, 2, 0.08])

    with col3:
        selected_competitions = sorted(filtered_df["League"].dropna().unique())

        if len(selected_competitions) == 1:
            competition_name = selected_competitions[0]
        elif len(selected_competitions) == 2:
            competition_name = " + ".join(selected_competitions)
        elif len(selected_competitions) > 2:
            competition_name = ", ".join(selected_competitions[:2]) + f" + {len(selected_competitions) - 2} more"
        else:
            competition_name = "All Competitions"

        st.subheader("Average Goals per Player")

        league_players_count = filtered_df[player_identity_column].nunique()
        league_goals_total = int(filtered_df["Goals"].sum()) if "Goals" in filtered_df.columns else 0

        avg_goals = (
            round(league_goals_total / league_players_count, 1)
            if league_players_count > 0
            else 0
        )

        gauge_max = max(10, avg_goals + 2)

        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=avg_goals,
                number={"font": {"size": 42, "color": TEXT_LIGHT}},
                title={
                    "text": f"Average Goals per Player<br><span style='font-size:16px;color:#B7FF3C'>{competition_name}</span>",
                    "font": {"size": 20, "color": TEXT_LIGHT},
                },
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
            paper_bgcolor=APP_BG,
            font=dict(color=TEXT_LIGHT),
            height=390,
            margin=dict(l=20, r=20, t=55, b=20)
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
        fig.add_trace(go.Bar(x=league_trends["League"], y=league_trends["Goals"], name="Goals", marker_color=BLUE,
                             text=league_trends["Goals"], textposition="inside"))
        fig.add_trace(go.Bar(x=league_trends["League"], y=league_trends["Assists"], name="Assists", marker_color=NEON,
                             text=league_trends["Assists"], textposition="inside"))
        fig.update_layout(title="Goals and Assists by League", xaxis_title="League", yaxis_title="Total",
                          barmode="stack")
        chart_layout(fig, 390)
        st.plotly_chart(fig, width="stretch")

    space_left, col5, gap, col6, space_right = st.columns([0.08, 1, 0.04, 1, 0.08])

    with col5:
        st.subheader("Players by Position")

        position_meanings = {
            "GK": "Goalkeeper",
            "DF": "Defender",
            "MF": "Midfielder",
            "FW": "Forward",
            "MF,FW": "Midfielder / Forward",
            "FW,MF": "Forward / Midfielder",
            "DF,MF": "Defender / Midfielder",
            "MF,DF": "Midfielder / Defender",
            "DF,FW": "Defender / Forward",
        }

        players_by_position = (
            filtered_df.groupby("Position", as_index=False)
            .agg({player_identity_column: "nunique"})
            .rename(columns={player_identity_column: "Number of Players"})
            .sort_values("Number of Players", ascending=False)
        )

        players_by_position["Position Meaning"] = (
            players_by_position["Position"]
            .map(position_meanings)
            .fillna("Mixed / Other")
        )

        players_by_position["Chart Label"] = (
                players_by_position["Position"]
                + " - "
                + players_by_position["Position Meaning"]
        )

        table_by_position = players_by_position[
            ["Position", "Position Meaning", "Number of Players"]
        ]

        centered_dataframe(table_by_position)

        fig = make_horizontal_bar(
            data=players_by_position,
            x_col="Number of Players",
            y_col="Chart Label",
            color_col="Position",
            title="Players by Position",
            x_title="Number of Players",
            y_title="Position",
            height=430,
            show_legend=False,
        )

        st.plotly_chart(fig, width="stretch")

    with col6:
        st.subheader("Yellow Cards by Club")
        cards_by_club = (
            filtered_df.groupby("Club", as_index=False)
            .agg({"Yellow Cards": "sum", "Red Cards": "sum"})
            .sort_values("Yellow Cards", ascending=False)
            .head(10)
        )
        centered_dataframe(cards_by_club)
        fig = go.Figure()
        fig.add_trace(
            go.Bar(y=cards_by_club["Club"], x=cards_by_club["Yellow Cards"], name="Yellow Cards", orientation="h",
                   marker_color=YELLOW, text=cards_by_club["Yellow Cards"], textposition="inside"))
        fig.add_trace(go.Bar(y=cards_by_club["Club"], x=cards_by_club["Red Cards"], name="Red Cards", orientation="h",
                             marker_color=RED, text=cards_by_club["Red Cards"], textposition="inside"))
        fig.update_layout(title="Yellow Cards by Club", xaxis_title="Cards", yaxis_title="Club", barmode="stack")
        fig.update_yaxes(autorange="reversed")
        chart_layout(fig, 430)
        st.plotly_chart(fig, width="stretch")

    space_left, col7, gap, col8, space_right = st.columns([0.08, 1, 0.04, 1, 0.08])

    reliable_players = filtered_df[
        filtered_df["Minutes Played"] >= 500
    ].copy()

    with col7:
        st.subheader("Shooting Performance")
        shooting_columns = [
            "Player Name", "Club", "Shots on Target per 90",
            "Shot Accuracy Percentage", "Goal Conversion Percentage",
        ]
        shooting_columns = [
            column for column in shooting_columns if column in reliable_players.columns
        ]
        shooting_df = (
            reliable_players.dropna(subset=["Shots on Target per 90"])
            .sort_values("Shots on Target per 90", ascending=False)
            .head(10)
        )
        centered_dataframe(shooting_df[shooting_columns])
        fig = make_horizontal_bar(
            shooting_df.sort_values("Shots on Target per 90"),
            "Shots on Target per 90",
            "Player Name",
            "Player Name",
            "Top Players by Shots on Target per 90",
            "Shots on target per 90",
            "Player",
            height=430,
            show_legend=False,
        )
        st.plotly_chart(fig, width="stretch")

    with col8:
        st.subheader("Defensive Contribution")
        defensive_columns = [
            "Player Name", "Club", "Tackles Won per 90",
            "Interceptions per 90", "Defensive Actions per 90",
        ]
        defensive_df = (
            reliable_players.dropna(subset=["Defensive Actions per 90"])
            .sort_values("Defensive Actions per 90", ascending=False)
            .head(10)
        )
        centered_dataframe(defensive_df[defensive_columns])
        fig = make_horizontal_bar(
            defensive_df.sort_values("Defensive Actions per 90"),
            "Defensive Actions per 90",
            "Player Name",
            "Player Name",
            "Top Players by Defensive Actions per 90",
            "Tackles won + interceptions per 90",
            "Player",
            height=430,
            show_legend=False,
        )
        st.plotly_chart(fig, width="stretch")


def show_competitions_page(filtered_df):
    """Show league comparison charts."""
    st.subheader("Competition Comparison")
    player_identity_column = (
        "Player ID" if "Player ID" in filtered_df.columns else "Player Name"
    )
    competition_df = (
        filtered_df.groupby("League", as_index=False)
        .agg({
            player_identity_column: "nunique",
            "Club": "nunique",
            "Goals": "sum",
            "Assists": "sum",
            "Matches Played": "sum",
            "Age": "mean"
        })
        .rename(columns={
            player_identity_column: "Players",
            "Club": "Clubs",
            "Matches Played": "Player Appearances",
            "Age": "Average Age"
        })
        .sort_values("Goals", ascending=False)
    )
    competition_df["Average Age"] = competition_df["Average Age"].round(1)
    centered_dataframe(competition_df)
    metric = st.selectbox(
        "Choose metric to compare",
        ["Players", "Clubs", "Goals", "Assists", "Player Appearances", "Average Age"]
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

    render_shortlist_quick_add(
        filtered_df,
        source_key="Players Light",
    )


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
        "Player Name", "Club", "Age", "Matches Played", "Minutes Played",
        "Shots on Target Against", "Saves", "Save Percentage",
        "Clean Sheets", "Clean Sheet Percentage", "Goals Against",
        "Goals Against per 90", "Penalty Save Percentage",
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


def show_similarity_page(filtered_df):
    """Show player similarity finder."""

    st.subheader("Player Similarity Finder")

    st.markdown(
        """
        <div style="color:#60758F; font-size:16px; font-weight:600; margin-bottom:14px;">
            Choose the player and decide which statistics should be used to calculate similarity.
            The model compares players using standardized values and cosine similarity.
        </div>
        """,
        unsafe_allow_html=True
    )

    available_features = get_available_similarity_features(filtered_df)

    default_features = [
        "Goals per 90",
        "Assists per 90",
        "Shots on Target per 90",
        "Crosses per 90",
        "Defensive Actions per 90",
    ]

    default_features = [
        feature for feature in default_features
        if feature in available_features
    ]

    selection_df = (
        filtered_df[["Player Record ID", "Player Selection Label"]]
        .dropna()
        .drop_duplicates("Player Record ID")
        .sort_values("Player Selection Label")
    )
    players = selection_df["Player Selection Label"].tolist()
    player_id_by_label = dict(
        zip(selection_df["Player Selection Label"], selection_df["Player Record ID"])
    )

    col1, col2, col3 = st.columns([1.5, 1, 1])

    with col1:
        selected_player_label = st.selectbox(
            "Choose a player",
            players
        )
        selected_player = player_id_by_label[selected_player_label]

    with col2:
        top_n = st.slider(
            "Number of similar players",
            min_value=5,
            max_value=20,
            value=10
        )

    with col3:
        min_minutes = st.slider(
            "Minimum minutes",
            min_value=0,
            max_value=4000,
            value=900,
            step=100
        )

    selected_features = st.multiselect(
        "Choose statistics for similarity calculation",
        options=available_features,
        default=default_features
    )

    same_position_only = st.checkbox(
        "Compare only players from the same position",
        value=True
    )

    if len(selected_features) == 0:
        st.warning("Please choose at least one statistic for similarity calculation.")
        return

    similar_players_df = find_similar_players(
        df=filtered_df,
        selected_player=selected_player,
        selected_features=selected_features,
        top_n=top_n,
        min_minutes=min_minutes,
        same_position_only=same_position_only
    )

    if similar_players_df is None:
        st.warning(
            "No similar players found. Try choosing different statistics, lowering the minimum minutes, or disabling same-position comparison."
        )
        return

    prepared_df = prepare_similarity_data(filtered_df)

    selected_player_df = prepared_df[
        prepared_df["Player Record ID"] == selected_player
        ].copy()

    st.markdown("### Selected Player")

    selected_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
        "Age",
        "Minutes Played",
        "Goals",
        "Assists",
        "Goals per 90",
        "Assists per 90",
        "Goals + Assists per 90",
    ]

    selected_columns = selected_columns + [
        feature for feature in selected_features
        if feature not in selected_columns
    ]

    selected_columns = [
        col for col in selected_columns
        if col in selected_player_df.columns
    ]

    centered_dataframe(selected_player_df[selected_columns])

    st.markdown("---")

    st.markdown(f"### Players most similar to **{selected_player_label}**")

    display_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
        "Similarity Score",
    ]

    display_columns = display_columns + [
        feature for feature in selected_features
        if feature not in display_columns
    ]

    display_columns = [
        col for col in display_columns
        if col in similar_players_df.columns
    ]

    centered_dataframe(similar_players_df[display_columns])

    shortlist_candidates = pd.concat(
        [selected_player_df, similar_players_df],
        ignore_index=True,
    ).drop_duplicates("Player Record ID")
    render_shortlist_quick_add(
        shortlist_candidates,
        source_key="Player Similarity Light",
        title="Save the selected player or a similar candidate",
    )


def show_clustering_page(filtered_df):
    """Show player clustering page with clearer explanations."""

    st.subheader("Player Clustering")

    st.markdown(
        """
        <div style="color:#60758F; font-size:16px; font-weight:600; margin-bottom:14px;">
            This page groups players into similar performance profiles using KMeans clustering.
            Instead of comparing one player to another, clustering finds groups of players who have similar statistics.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Simple meaning: players inside the same cluster have similar profiles based on the statistics you choose."
    )

    available_features = get_available_clustering_features(filtered_df)

    default_features = [
        "Goals per 90",
        "Assists per 90",
        "Shots on Target per 90",
        "Crosses per 90",
        "Defensive Actions per 90",
    ]

    default_features = [
        feature for feature in default_features
        if feature in available_features
    ]

    col1, col2 = st.columns(2)

    with col1:
        number_of_clusters = st.slider(
            "How many player groups do you want?",
            min_value=2,
            max_value=8,
            value=4,
            help="Example: 4 means the model will divide players into 4 different profile groups."
        )

    with col2:
        min_minutes = st.slider(
            "Minimum minutes played",
            min_value=0,
            max_value=4000,
            value=900,
            step=100,
            help="Higher minutes gives more reliable groups because very low-minute players can distort the results."
        )

    selected_features = st.multiselect(
        "Choose statistics used to create the player groups",
        options=available_features,
        default=default_features,
        help="The model uses only these selected statistics to decide which players are similar."
    )

    if len(selected_features) == 0:
        st.warning("Please choose at least one statistic for clustering.")
        return

    clustered_df, cluster_summary = cluster_players(
        df=filtered_df,
        selected_features=selected_features,
        number_of_clusters=number_of_clusters,
        min_minutes=min_minutes
    )

    if clustered_df is None:
        st.warning(
            "Not enough players for clustering. Try lowering the minimum minutes or selecting fewer clusters."
        )
        return

    cluster_summary = describe_cluster_profiles(
        cluster_summary=cluster_summary,
        selected_features=selected_features
    )

    clustered_df = clustered_df.merge(
        cluster_summary[["Cluster", "Cluster Profile"]],
        on="Cluster",
        how="left"
    )

    st.markdown("### What each cluster means")

    explanation_columns = [
        "Cluster",
        "Cluster Profile",
        "Number of Players",
        "Description",
    ]

    explanation_columns = [
        col for col in explanation_columns
        if col in cluster_summary.columns
    ]

    centered_dataframe(cluster_summary[explanation_columns])

    st.markdown("---")

    st.markdown("### Cluster Summary with Averages")

    st.caption(
        "This table shows the average values of each selected statistic inside every cluster."
    )

    summary_columns = [
                          "Cluster",
                          "Cluster Profile",
                          "Number of Players",
                      ] + selected_features

    summary_columns = [
        col for col in summary_columns
        if col in cluster_summary.columns
    ]

    centered_dataframe(cluster_summary[summary_columns])

    st.markdown("---")

    st.markdown("### Player Groups Overview")

    st.caption(
        "This chart shows how many players are inside each cluster. "
        "The X-axis shows the player group created by the clustering model. "
        "The Y-axis shows how many players belong to that group."
    )

    import plotly.express as px

    cluster_chart_df = (
        clustered_df.groupby(["Cluster", "Cluster Profile"], as_index=False)
        .agg({"Player Name": "nunique"})
        .rename(columns={"Player Name": "Number of Players"})
        .sort_values("Number of Players", ascending=False)
    )

    cluster_chart_df["Cluster Label"] = (
            "Cluster "
            + cluster_chart_df["Cluster"].astype(str)
            + " — "
            + cluster_chart_df["Cluster Profile"]
    )

    fig = px.bar(
        cluster_chart_df,
        x="Cluster Label",
        y="Number of Players",
        text="Number of Players",
        color="Cluster Profile",
        title="Number of Players in Each Cluster",
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title="Player group / cluster",
        yaxis_title="Number of players in this group",
        height=520,
        showlegend=False,
    )

    chart_layout(fig, 520)

    st.plotly_chart(fig, width="stretch")

    st.markdown("### Compare One Statistic Across Clusters")

    st.caption(
        "Choose one statistic to see the average value for each cluster. "
        "The X-axis shows the player group. "
        "The Y-axis shows the average value of the selected statistic inside that group."
    )

    selected_metric_for_chart = st.selectbox(
        "Choose statistic to compare across clusters",
        selected_features
    )

    metric_chart_df = cluster_summary[
        ["Cluster", "Cluster Profile", selected_metric_for_chart]
    ].copy()

    metric_chart_df["Cluster Label"] = (
            "Cluster "
            + metric_chart_df["Cluster"].astype(str)
            + " — "
            + metric_chart_df["Cluster Profile"]
    )

    metric_chart_df = metric_chart_df.sort_values(
        selected_metric_for_chart,
        ascending=False
    )

    fig_metric = px.bar(
        metric_chart_df,
        x="Cluster Label",
        y=selected_metric_for_chart,
        text=selected_metric_for_chart,
        color="Cluster Profile",
        title=f"Average {selected_metric_for_chart} by Cluster",
    )

    fig_metric.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_metric.update_layout(
        xaxis_title="Player group / cluster",
        yaxis_title=f"Average {selected_metric_for_chart}",
        height=520,
        showlegend=False,
    )

    chart_layout(fig_metric, 520)

    st.plotly_chart(fig_metric, width="stretch")

    st.markdown("---")

    st.markdown("### Scatter Plot: Compare Two Statistics")

    st.caption(
        "This scatter plot compares two real football statistics. "
        "Each dot is one player. The X-axis is the first statistic you choose, "
        "and the Y-axis is the second statistic you choose. "
        "Players with similar values will appear closer together."
    )

    scatter_col1, scatter_col2 = st.columns(2)

    with scatter_col1:
        x_metric = st.selectbox(
            "Choose X-axis statistic",
            selected_features,
            index=0
        )

    with scatter_col2:
        y_metric_default_index = 1 if len(selected_features) > 1 else 0

        y_metric = st.selectbox(
            "Choose Y-axis statistic",
            selected_features,
            index=y_metric_default_index
        )

    scatter_df = clustered_df.dropna(
        subset=[x_metric, y_metric]
    ).copy()

    if scatter_df.empty:
        st.warning(
            "No data available for the selected X-axis and Y-axis statistics."
        )
    else:
        fig_scatter = px.scatter(
            scatter_df,
            x=x_metric,
            y=y_metric,
            color="Cluster Profile",
            hover_name="Player Name",
            hover_data=[
                "Cluster",
                "Club",
                "League",
                "Position",
                "Age",
                "Minutes Played",
                "Goals",
                "Assists",
            ],
            title=f"{x_metric} vs {y_metric} by Player Group",
        )

        fig_scatter.update_layout(
            xaxis_title=f"{x_metric}",
            yaxis_title=f"{y_metric}",
            height=600,
            legend_title_text="Player group",
        )

        chart_layout(fig_scatter, 600)

        st.plotly_chart(fig_scatter, width="stretch")


def show_radar_page(filtered_df):
    """Show radar chart player comparison page."""

    st.subheader("Radar Chart Player Comparison")

    st.markdown(
        """
        <div style="color:#60758F; font-size:16px; font-weight:600; margin-bottom:14px;">
            Compare multiple players using a radar chart. Each metric is normalized from 0 to 100,
            so different statistics can be compared in one visual.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Simple meaning: the larger the shape, the stronger the player is across the selected statistics."
    )

    available_features = get_available_radar_features(filtered_df)

    default_features = [
        "Goals per 90",
        "Assists per 90",
        "Shots on Target per 90",
        "Crosses per 90",
        "Defensive Actions per 90",
    ]

    default_features = [
        feature for feature in default_features
        if feature in available_features
    ]

    selection_df = (
        filtered_df[["Player Record ID", "Player Selection Label"]]
        .dropna()
        .drop_duplicates("Player Record ID")
        .sort_values("Player Selection Label")
    )
    players = selection_df["Player Selection Label"].tolist()
    player_id_by_label = dict(
        zip(selection_df["Player Selection Label"], selection_df["Player Record ID"])
    )

    selected_players = st.multiselect(
        "Choose players to compare",
        options=players,
        default=players[:2] if len(players) >= 2 else players,
        help="Choose 2 to 5 players for the clearest radar chart."
    )

    col1, col2 = st.columns(2)

    with col1:
        selected_features = st.multiselect(
            "Choose statistics for radar chart",
            options=available_features,
            default=default_features,
            help="The radar chart will compare players using these metrics."
        )

    with col2:
        min_minutes = st.slider(
            "Minimum minutes for scaling",
            min_value=0,
            max_value=4000,
            value=900,
            step=100,
            help="The normalization uses players above this minutes limit."
        )

    if len(selected_players) < 2:
        st.warning("Please choose at least two players to compare.")
        return

    if len(selected_players) > 5:
        st.warning("For a readable radar chart, please choose maximum 5 players.")
        return

    if len(selected_features) < 3:
        st.warning("Please choose at least three statistics for the radar chart.")
        return

    radar_normalized_df, original_values_df = create_radar_comparison_data(
        df=filtered_df,
        selected_players=[player_id_by_label[player] for player in selected_players],
        selected_features=selected_features,
        min_minutes=min_minutes
    )

    if radar_normalized_df is None:
        st.warning(
            "No radar data available. Try lowering the minimum minutes or choosing different players/statistics."
        )
        return

    st.markdown("### Radar Chart")

    st.caption(
        "Each axis is one selected statistic. Values are scaled from 0 to 100. "
        "A value near 100 means the player is strong in that metric compared with the filtered dataset."
    )

    import plotly.graph_objects as go

    fig = go.Figure()

    for _, row in radar_normalized_df.iterrows():
        values = [row[feature] for feature in selected_features]
        values.append(values[0])

        categories = selected_features.copy()
        categories.append(selected_features[0])

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name=row.get("Player Selection Label", row["Player Name"]),
                hovertemplate="<b>%{theta}</b><br>Score: %{r:.1f}/100<extra></extra>",
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color="#D4E2F5"),
                gridcolor="rgba(212,226,245,0.25)",
            ),
            angularaxis=dict(
                tickfont=dict(color="#EAF2FF", size=12),
                gridcolor="rgba(212,226,245,0.25)",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#EAF2FF"),
        height=650,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(l=40, r=40, t=40, b=90),
    )

    st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    st.markdown("### Selected Players — Original Values")

    st.caption(
        "This table shows the real football values before normalization. "
        "Use this table to understand the actual numbers behind the radar chart."
    )

    display_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
        "Age",
        "Minutes Played",
        "Goals",
        "Assists",
    ]

    display_columns = display_columns + [
        feature for feature in selected_features
        if feature not in display_columns
    ]

    display_columns = [
        col for col in display_columns
        if col in original_values_df.columns
    ]

    centered_dataframe(original_values_df[display_columns])

    st.markdown("---")

    st.markdown("### Selected Players — Radar Scores")

    st.caption(
        "These are normalized scores from 0 to 100. They are used only for the radar chart."
    )

    score_columns = [
                        "Player Name",
                        "Club",
                        "League",
                        "Position",
                    ] + selected_features

    score_columns = [
        col for col in score_columns
        if col in radar_normalized_df.columns
    ]

    centered_dataframe(radar_normalized_df[score_columns])


def show_scouting_page(filtered_df):
    """Show player scoring and young talent detection page."""

    st.subheader("Scouting & Talent Finder")

    st.markdown(
        """
        <div style="color:#60758F; font-size:16px; font-weight:600; margin-bottom:14px;">
            This page ranks players using a custom scoring system and highlights young talents.
            You can change the weights to decide what matters most: goals, assists, expected output, or progression.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Simple meaning: Player Score ranks overall performance. Young Talent Score ranks young players based on performance, age, and playing time."
    )

    render_shortlist_quick_add(
        filtered_df,
        source_key="Scouting Light",
        title="Save a scouting candidate to the transfer shortlist",
    )

    tab1, tab2, tab3 = st.tabs([
        "Player Scoring System",
        "Young Talent Detection",
        "Role-Specific Score",
    ])

    with tab1:
        st.markdown("### Player Scoring System")

        st.caption(
            "The Player Score is calculated from normalized football metrics. "
            "Each metric is converted to a 0–100 score, then combined using your selected weights."
        )

        col1, col2 = st.columns(2)

        with col1:
            min_minutes = st.slider(
                "Minimum minutes for player scoring",
                min_value=0,
                max_value=4000,
                value=900,
                step=100
            )

            top_n_players = st.slider(
                "Number of top players to show",
                min_value=5,
                max_value=50,
                value=20
            )

        with col2:
            st.markdown("#### Score Weights")

            goal_weight = st.slider(
                "Goals weight",
                min_value=0,
                max_value=100,
                value=35
            )

            assist_weight = st.slider(
                "Assists weight",
                min_value=0,
                max_value=100,
                value=25
            )

            xg_weight = st.slider(
                "Expected output weight",
                min_value=0,
                max_value=100,
                value=20
            )

            progression_weight = st.slider(
                "Progression weight",
                min_value=0,
                max_value=100,
                value=20
            )

        scored_players = calculate_player_scores(
            df=filtered_df,
            min_minutes=min_minutes,
            goal_weight=goal_weight,
            assist_weight=assist_weight,
            xg_weight=xg_weight,
            progression_weight=progression_weight
        )

        if scored_players is None or scored_players.empty:
            st.warning(
                "No players available for scoring. Try lowering the minimum minutes."
            )
        else:
            st.markdown("### Top Players by Player Score")

            display_columns = [
                "Player Name",
                "Nationality",
                "Position",
                "Club",
                "League",
                "Age",
                "Minutes Played",
                "Goals",
                "Assists",
                "Goals per 90",
                "Assists per 90",
                "Expected Goals + Expected Assists per 90",
                "Progressive Carries per 90",
                "Progressive Passes per 90",
                "Score Coverage %",
                "Score Components Used",
                "Player Score",
            ]

            display_columns = [
                col for col in display_columns
                if col in scored_players.columns
            ]

            centered_dataframe(
                scored_players[display_columns].head(top_n_players)
            )

            st.markdown("---")

            st.markdown("### Player Score Chart")

            st.caption(
                "The X-axis shows the final Player Score. "
                "The Y-axis shows the player name. Higher score means stronger overall performance based on your selected weights."
            )

            import plotly.express as px

            chart_df = scored_players.head(top_n_players).copy()

            chart_df["Player Label"] = (
                    chart_df["Player Name"]
                    + " — "
                    + chart_df["Club"]
            )

            chart_df = chart_df.sort_values(
                "Player Score",
                ascending=True
            )

            fig = px.bar(
                chart_df,
                x="Player Score",
                y="Player Label",
                orientation="h",
                text="Player Score",
                color="Player Score",
                title="Top Players by Custom Player Score",
            )

            fig.update_traces(
                textposition="outside"
            )

            fig.update_layout(
                xaxis_title="Player Score from 0 to 100",
                yaxis_title="Player",
                height=650,
                showlegend=False,
            )

            chart_layout(fig, 650)

            st.plotly_chart(fig, width="stretch")

    with tab2:
        st.markdown("### Young Talent Detection")

        st.caption(
            "Young Talent Score highlights young players with strong performance, good playing time, and high potential."
        )

        col1, col2 = st.columns(2)

        with col1:
            max_age = st.slider(
                "Maximum age for young talents",
                min_value=18,
                max_value=26,
                value=23
            )

            min_minutes_talent = st.slider(
                "Minimum minutes for young talents",
                min_value=0,
                max_value=3000,
                value=500,
                step=100
            )

            top_n_talents = st.slider(
                "Number of young talents to show",
                min_value=5,
                max_value=50,
                value=20
            )

        with col2:
            st.markdown("#### Talent Score Weights")

            performance_weight = st.slider(
                "Performance weight",
                min_value=0,
                max_value=100,
                value=60
            )

            age_weight = st.slider(
                "Age potential weight",
                min_value=0,
                max_value=100,
                value=25
            )

            minutes_weight = st.slider(
                "Playing time weight",
                min_value=0,
                max_value=100,
                value=15
            )

        young_talents = calculate_young_talent_scores(
            df=filtered_df,
            max_age=max_age,
            min_minutes=min_minutes_talent,
            performance_weight=performance_weight,
            age_weight=age_weight,
            minutes_weight=minutes_weight
        )

        if young_talents is None or young_talents.empty:
            st.warning(
                "No young talents found. Try increasing maximum age or lowering minimum minutes."
            )
        else:
            st.markdown("### Top Young Talents")

            talent_columns = [
                "Player Name",
                "Nationality",
                "Position",
                "Club",
                "League",
                "Age",
                "Minutes Played",
                "Goals",
                "Assists",
                "Goals per 90",
                "Assists per 90",
                "Player Score",
                "Young Talent Score",
            ]

            talent_columns = [
                col for col in talent_columns
                if col in young_talents.columns
            ]

            centered_dataframe(
                young_talents[talent_columns].head(top_n_talents)
            )

            st.markdown("---")

            st.markdown("### Young Talent Score Chart")

            st.caption(
                "The X-axis shows the Young Talent Score. "
                "The Y-axis shows young players. Higher score means stronger talent profile based on performance, age, and minutes."
            )

            import plotly.express as px

            talent_chart_df = young_talents.head(top_n_talents).copy()

            talent_chart_df["Player Label"] = (
                    talent_chart_df["Player Name"]
                    + " — "
                    + talent_chart_df["Club"]
            )

            talent_chart_df = talent_chart_df.sort_values(
                "Young Talent Score",
                ascending=True
            )

            fig_talent = px.bar(
                talent_chart_df,
                x="Young Talent Score",
                y="Player Label",
                orientation="h",
                text="Young Talent Score",
                color="Young Talent Score",
                title="Top Young Talents by Talent Score",
            )

            fig_talent.update_traces(
                textposition="outside"
            )

            fig_talent.update_layout(
                xaxis_title="Young Talent Score from 0 to 100",
                yaxis_title="Young player",
                height=650,
                showlegend=False,
            )

            chart_layout(fig_talent, 650)

            st.plotly_chart(fig_talent, width="stretch")

    with tab3:
        st.markdown("### Role-Specific Player Ranking")

        st.caption(
            "Players are compared only with peers in their primary position. "
            "Forwards, midfielders, defenders and goalkeepers use different metrics."
        )

        min_minutes_role = st.slider(
            "Minimum minutes for role-specific ranking",
            min_value=0,
            max_value=4000,
            value=900,
            step=100,
        )

        role_scores = calculate_role_percentile_scores(
            filtered_df,
            min_minutes=min_minutes_role,
        )

        if role_scores is None or role_scores.empty:
            st.warning("No role-specific scores are available for the selected filters.")
        else:
            role_labels = {
                "FW": "Forwards",
                "MF": "Midfielders",
                "DF": "Defenders",
                "GK": "Goalkeepers",
            }
            available_roles = [
                role for role in ["FW", "MF", "DF", "GK"]
                if role in role_scores["Primary Position"].values
            ]
            selected_role = st.selectbox(
                "Choose role",
                available_roles,
                format_func=lambda role: role_labels.get(role, role),
            )

            role_table = role_scores[
                role_scores["Primary Position"] == selected_role
            ].sort_values("Role Score", ascending=False)

            role_metrics = [
                metric
                for metric, _, _ in ROLE_SCORE_PROFILES[selected_role]
                if metric in role_table.columns
            ]
            role_columns = [
                "Role Rank",
                "Player Name",
                "Club",
                "League",
                "Age",
                "Minutes Played",
                "Role Score",
                "Role Score Coverage %",
            ] + role_metrics

            centered_dataframe(role_table[role_columns].head(30))

            import plotly.express as px

            chart_df = role_table.head(20).sort_values("Role Score").copy()
            fig_role = px.bar(
                chart_df,
                x="Role Score",
                y="Player Selection Label",
                orientation="h",
                text="Role Score",
                color="Role Score",
                title=f"Top {role_labels.get(selected_role, selected_role)} by Role Score",
            )
            fig_role.update_traces(textposition="outside")
            fig_role.update_layout(
                xaxis_title="Position-relative percentile score (0–100)",
                yaxis_title="Player",
                height=650,
                showlegend=False,
            )
            chart_layout(fig_role, 650)
            st.plotly_chart(fig_role, width="stretch")

            with st.expander("Role score methodology"):
                st.write(
                    "Each metric is converted to a percentile inside the selected "
                    "position cohort. Lower-is-better discipline and goals-against "
                    "metrics are reversed. Missing values reduce coverage instead "
                    "of being treated as zero."
                )
                st.write(ROLE_SCORE_PROFILES[selected_role])


def show_transfer_shortlist_page(players_df):
    """Show the light-theme recruitment workspace."""

    show_shared_transfer_shortlist_page(players_df, theme="light")


def show_league_analysis_page(filtered_df):
    """Show advanced league comparison analysis."""

    st.subheader("League Comparison Analysis")

    st.markdown(
        """
        <div style="color:#60758F; font-size:16px; font-weight:600; margin-bottom:14px;">
            Compare leagues by attacking output, shooting, defensive actions, player volume,
            average age, assists, and discipline. Optional xG metrics appear when available.
        </div>
        """,
        unsafe_allow_html=True
    )

    league_summary = create_league_summary(filtered_df)

    if league_summary.empty:
        st.warning("No league data available for the selected filters.")
        return

    st.markdown("### League Summary Table")

    st.caption(
        "This table compares each league using totals and averages. "
        "Totals show league volume, while per-90 values show average player efficiency."
    )

    centered_dataframe(league_summary)

    st.markdown("---")

    st.markdown("### Compare Leagues by One Metric")

    metric_options = [
        col for col in league_summary.columns
        if col != "League"
           and pd.api.types.is_numeric_dtype(league_summary[col])
    ]

    selected_metric = st.selectbox(
        "Choose metric to compare",
        metric_options
    )

    chart_df = league_summary.sort_values(
        selected_metric,
        ascending=True
    )

    import plotly.express as px

    fig = px.bar(
        chart_df,
        x=selected_metric,
        y="League",
        orientation="h",
        text=selected_metric,
        color="League",
        title=f"League Comparison by {selected_metric}",
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        xaxis_title=selected_metric,
        yaxis_title="League",
        height=520,
        showlegend=False,
    )

    chart_layout(fig, 520)

    st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    st.markdown("### Goals vs Assists by League")

    st.caption(
        "This chart compares total goals and total assists across leagues. "
        "The X-axis shows the league. The Y-axis shows the total number of actions."
    )

    if "Goals" in league_summary.columns and "Assists" in league_summary.columns:
        goals_assists_df = league_summary[
            ["League", "Goals", "Assists"]
        ].copy()

        goals_assists_long = goals_assists_df.melt(
            id_vars="League",
            value_vars=["Goals", "Assists"],
            var_name="Metric",
            value_name="Total"
        )

        fig_goals_assists = px.bar(
            goals_assists_long,
            x="League",
            y="Total",
            color="Metric",
            barmode="group",
            text="Total",
            title="Goals and Assists by League",
        )

        fig_goals_assists.update_traces(
            textposition="outside"
        )

        fig_goals_assists.update_layout(
            xaxis_title="League",
            yaxis_title="Total goals / assists",
            height=520,
        )

        chart_layout(fig_goals_assists, 520)

        st.plotly_chart(fig_goals_assists, width="stretch")
    else:
        st.info("Goals and assists columns are not available.")

    st.markdown("---")

    st.markdown("### Player Position Distribution by League")

    position_summary = create_league_position_summary(filtered_df)

    if position_summary is None or position_summary.empty:
        st.info("Position summary is not available.")
        return

    selected_league_for_position = st.selectbox(
        "Choose league for position distribution",
        sorted(position_summary["League"].unique())
    )

    position_chart_df = position_summary[
        position_summary["League"] == selected_league_for_position
        ].copy()

    position_chart_df = position_chart_df.sort_values(
        "Number of Players",
        ascending=True
    )

    fig_position = px.bar(
        position_chart_df,
        x="Number of Players",
        y="Position",
        orientation="h",
        text="Number of Players",
        color="Position",
        title=f"Player Positions in {selected_league_for_position}",
    )

    fig_position.update_traces(
        textposition="outside"
    )

    fig_position.update_layout(
        xaxis_title="Number of players",
        yaxis_title="Position",
        height=480,
        showlegend=False,
    )

    chart_layout(fig_position, 480)

    st.plotly_chart(fig_position, width="stretch")


def show_pca_page(filtered_df):
    """Show PCA player profile analysis."""

    st.subheader("Player Profile Map")

    st.markdown(
        """
        <div style="color:#60758F; font-size:16px; font-weight:600; margin-bottom:14px;">
            This page creates a visual map of player profiles. 
            Players close to each other have similar statistics, while players far apart have different playing profiles.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Simple meaning: players close together on the chart have similar statistical profiles based on the metrics you choose."
    )

    available_features = get_available_pca_features(filtered_df)

    default_features = [
        "Goals per 90",
        "Assists per 90",
        "Shots on Target per 90",
        "Crosses per 90",
        "Defensive Actions per 90",
    ]

    default_features = [
        feature for feature in default_features
        if feature in available_features
    ]

    col1, col2 = st.columns(2)

    with col1:
        min_minutes = st.slider(
            "Minimum minutes",
            min_value=0,
            max_value=4000,
            value=900,
            step=100
        )

    with col2:
        color_by = st.selectbox(
            "Color players by",
            [
                "Position",
                "League",
                "Club",
            ]
        )

    selected_features = st.multiselect(
        "Choose statistics for PCA",
        options=available_features,
        default=default_features
    )

    if len(selected_features) < 2:
        st.warning("Please choose at least two statistics for PCA.")
        return

    pca_df, explained_variance, component_loadings = create_player_pca(
        df=filtered_df,
        selected_features=selected_features,
        min_minutes=min_minutes
    )

    if pca_df is None:
        st.warning(
            "Not enough data for PCA. Try lowering minimum minutes or choosing different statistics."
        )
        return

    st.markdown("### PCA Explanation")

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric(
            "PCA 1 Explained Variance",
            f"{explained_variance['PCA 1 Explained Variance %']}%"
        )

    with k2:
        st.metric(
            "PCA 2 Explained Variance",
            f"{explained_variance['PCA 2 Explained Variance %']}%"
        )

    with k3:
        st.metric(
            "Total Explained Variance",
            f"{explained_variance['Total Explained Variance %']}%"
        )

    st.caption(
        "Explained variance shows how much information from the selected statistics is captured by the two PCA axes."
    )

    st.markdown("---")

    st.markdown("### Player Profile Map")

    st.caption(
        "Each dot is one player. Players close to each other have similar profiles. "
        "The X-axis and Y-axis are PCA components created from the selected statistics."
    )

    import plotly.express as px

    hover_columns = [
        "Player Name",
        "Club",
        "League",
        "Position",
        "Age",
        "Minutes Played",
        "Goals",
        "Assists",
    ]

    hover_columns = [
        col for col in hover_columns
        if col in pca_df.columns
    ]

    fig = px.scatter(
        pca_df,
        x="PCA 1",
        y="PCA 2",
        color=color_by,
        hover_name="Player Name",
        hover_data=hover_columns,
        title="PCA Player Profile Map",
    )

    fig.update_layout(
        xaxis_title="PCA 1 — strongest combined profile direction",
        yaxis_title="PCA 2 — second strongest profile difference",
        height=650,
        legend_title_text=color_by,
    )

    chart_layout(fig, 650)

    st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    st.markdown("### What Influences PCA 1 and PCA 2?")

    st.caption(
        "This table shows which original statistics influence each PCA direction. "
        "Positive and negative values show how strongly each statistic contributes."
    )

    centered_dataframe(component_loadings)

    st.markdown("---")

    st.markdown("### Player PCA Data")

    display_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
        "Age",
        "Minutes Played",
        "Goals",
        "Assists",
        "PCA 1",
        "PCA 2",
    ]

    display_columns = display_columns + [
        feature for feature in selected_features
        if feature not in display_columns
    ]

    display_columns = [
        col for col in display_columns
        if col in pca_df.columns
    ]

    centered_dataframe(pca_df[display_columns])


def show_predictions_page(filtered_df):
    """Show predictive models and advanced football metrics."""

    st.subheader("Predictions & Advanced Metrics")

    st.markdown(
        """
        <div style="color:#60758F; font-size:16px; font-weight:600; margin-bottom:14px;">
            This page adds machine learning predictions and advanced football metrics.
            You can estimate same-season goal output, classify top performers, and analyze available performance metrics.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Simple meaning: the prediction models learn patterns from the current dataset. "
        "The advanced metrics explain how efficient players are compared with their expected output."
    )

    tab1, tab2, tab3 = st.tabs([
        "Predict Goals",
        "Top Performer Classifier",
        "Advanced Metrics"
    ])

    with tab1:
        st.markdown("### Option A: Predict Player Goals")

        st.caption(
            "This model estimates same-season goals from position, league, assists, shooting, and other available metrics. "
            "It is not a next-season forecast."
        )

        min_minutes_goals = st.slider(
            "Minimum minutes for goal prediction",
            min_value=0,
            max_value=4000,
            value=500,
            step=100
        )

        goal_predictions, goal_metrics, goal_features = train_goals_prediction_model(
            df=filtered_df,
            min_minutes=min_minutes_goals
        )

        if goal_predictions is None:
            st.warning(
                "Not enough data for goal prediction. Try lowering the minimum minutes filter."
            )
        else:
            st.markdown("#### Model Performance")

            c1, c2, c3, c4, c5, c6 = st.columns(6)

            with c1:
                st.metric("MAE", goal_metrics["MAE"])

            with c2:
                st.metric("RMSE", goal_metrics["RMSE"])

            with c3:
                st.metric("R² Score", goal_metrics["R2 Score"])

            with c4:
                st.metric("Baseline MAE", goal_metrics["Baseline MAE"])

            with c5:
                st.metric("Training Rows", goal_metrics["Training Rows"])

            with c6:
                st.metric("Test Rows", goal_metrics["Test Rows"])

            st.caption(
                "MAE means the average prediction error in goals. "
                "Lower MAE is better. R² shows how much variance the model explains."
            )

            st.markdown("#### Predicted Goals Table")

            display_columns = [
                "Player Name",
                "Nationality",
                "Position",
                "Club",
                "League",
                "Age",
                "Minutes Played",
                "Goals",
                "Predicted Goals",
                "Goal Difference vs Prediction",
                "Assists",
                "Expected Goals",
                "Expected Assisted Goals",
            ]

            display_columns = [
                col for col in display_columns
                if col in goal_predictions.columns
            ]

            centered_dataframe(
                goal_predictions[display_columns].head(30)
            )

            st.markdown("---")

            st.markdown("#### Predicted Goals Chart")

            st.caption(
                "The X-axis shows predicted goals. "
                "The Y-axis shows players. Higher predicted goals means the model expects stronger goal output."
            )

            import plotly.express as px

            chart_df = goal_predictions.head(20).copy()

            chart_df["Player Label"] = (
                    chart_df["Player Name"]
                    + " — "
                    + chart_df["Club"]
            )

            chart_df = chart_df.sort_values(
                "Predicted Goals",
                ascending=True
            )

            fig = px.bar(
                chart_df,
                x="Predicted Goals",
                y="Player Label",
                orientation="h",
                text="Predicted Goals",
                color="Predicted Goals",
                title="Top Players by Predicted Goals",
            )

            fig.update_traces(textposition="outside")

            fig.update_layout(
                xaxis_title="Predicted goals",
                yaxis_title="Player",
                height=650,
                showlegend=False,
            )

            chart_layout(fig, 650)

            st.plotly_chart(fig, width="stretch")

            with st.expander("Model features used"):
                st.write(goal_features)

    with tab2:
        st.markdown("### Option B: Predict Top Performers")

        st.caption(
            "This model predicts whether a player belongs to the top performance group. "
            "The target is based on Goals + Assists per 90."
        )

        col1, col2 = st.columns(2)

        with col1:
            min_minutes_classifier = st.slider(
                "Minimum minutes for classifier",
                min_value=0,
                max_value=4000,
                value=500,
                step=100
            )

        with col2:
            top_percentile = st.slider(
                "Top performer percentile",
                min_value=60,
                max_value=90,
                value=75,
                step=5,
                help="75 means players in the top 25% by Goals + Assists per 90 are labeled as top performers."
            )

        classifier_results, classifier_metrics, classifier_features = train_top_performer_classifier(
            df=filtered_df,
            min_minutes=min_minutes_classifier,
            top_percentile=top_percentile
        )

        if classifier_results is None:
            st.warning(
                "Not enough data for top performer classification. Try lowering the minimum minutes filter."
            )
        else:
            st.markdown("#### Model Performance")

            c1, c2, c3, c4, c5 = st.columns(5)

            with c1:
                st.metric("Accuracy", classifier_metrics["Accuracy"])

            with c2:
                st.metric("Baseline Accuracy", classifier_metrics["Baseline Accuracy"])

            with c3:
                st.metric("Balanced Accuracy", classifier_metrics["Balanced Accuracy"])

            with c4:
                st.metric("F1 Score", classifier_metrics["F1 Score"])

            with c5:
                st.metric("ROC AUC", classifier_metrics["ROC AUC"])

            st.caption(
                f"Precision: {classifier_metrics['Precision']} · Recall: {classifier_metrics['Recall']} · "
                f"Top threshold: {classifier_metrics['Top Performer Threshold']} · "
                f"Training rows: {classifier_metrics['Training Rows']} · Test rows: {classifier_metrics['Test Rows']}. "
                "Compare model accuracy with baseline accuracy before judging performance."
            )

            st.markdown("#### Top Performer Probability Table")

            display_columns = [
                "Player Name",
                "Nationality",
                "Position",
                "Club",
                "League",
                "Age",
                "Minutes Played",
                "Goals",
                "Assists",
                "Goals + Assists per 90",
                "Top Performer Probability",
                "Predicted Label",
            ]

            display_columns = [
                col for col in display_columns
                if col in classifier_results.columns
            ]

            centered_dataframe(
                classifier_results[display_columns].head(30)
            )

            st.markdown("---")

            st.markdown("#### Top Performer Probability Chart")

            st.caption(
                "The X-axis shows the probability that the player is a top performer. "
                "The Y-axis shows players. Higher probability means stronger predicted top-player profile."
            )

            import plotly.express as px

            chart_df = classifier_results.head(20).copy()

            chart_df["Player Label"] = (
                    chart_df["Player Name"]
                    + " — "
                    + chart_df["Club"]
            )

            chart_df = chart_df.sort_values(
                "Top Performer Probability",
                ascending=True
            )

            fig_classifier = px.bar(
                chart_df,
                x="Top Performer Probability",
                y="Player Label",
                orientation="h",
                text="Top Performer Probability",
                color="Top Performer Probability",
                title="Top Players by Top Performer Probability",
            )

            fig_classifier.update_traces(textposition="outside")

            fig_classifier.update_layout(
                xaxis_title="Top performer probability (%)",
                yaxis_title="Player",
                height=650,
                showlegend=False,
            )

            chart_layout(fig_classifier, 650)

            st.plotly_chart(fig_classifier, width="stretch")

            with st.expander("Model features used"):
                st.write(classifier_features)

    with tab3:
        st.markdown("### Advanced Football Metrics")

        st.caption(
            "This section shows shooting, creative, defensive, discipline and goalkeeper metrics. "
            "xG metrics appear automatically when the loaded dataset contains xG columns."
        )

        min_minutes_metrics = st.slider(
            "Minimum minutes for advanced metrics",
            min_value=0,
            max_value=4000,
            value=500,
            step=100
        )

        advanced_metrics = create_advanced_metrics_table(
            df=filtered_df,
            min_minutes=min_minutes_metrics
        )

        if advanced_metrics is None or advanced_metrics.empty:
            st.warning(
                "No advanced metrics available. Try lowering the minimum minutes filter."
            )
        else:
            metric_columns = [
                "Player Name",
                "Nationality",
                "Position",
                "Club",
                "League",
                "Age",
                "Minutes Played",
                "Goals",
                "Assists",
                "Expected Goals",
                "Expected Assisted Goals",
                "Goals minus xG",
                "Goal Efficiency Ratio",
                "Assists minus xAG",
                "Goals per 90",
                "Assists per 90",
                "Goals + Assists per 90",
                "Shots per 90",
                "Shots on Target per 90",
                "Shot Accuracy Percentage",
                "Goal Conversion Percentage",
                "Crosses per 90",
                "Tackles Won per 90",
                "Interceptions per 90",
                "Defensive Actions per 90",
                "Fouled per 90",
                "Fouls Committed per 90",
                "Save Percentage",
                "Clean Sheet Percentage",
                "Penalty Save Percentage",
                "Expected Goals per 90",
                "Expected Assisted Goals per 90",
                "Expected Goals + Expected Assists per 90",
                "Progressive Carries per 90",
                "Progressive Passes per 90",
                "Total Progressive Actions",
                "Discipline Risk",
            ]

            metric_columns = [
                col for col in metric_columns
                if col in advanced_metrics.columns
            ]

            st.markdown("#### Advanced Metrics Table")

            centered_dataframe(
                advanced_metrics[metric_columns].head(50)
            )

            st.markdown("---")

            st.markdown("#### xG Efficiency Chart")

            st.caption(
                "The X-axis shows Goals minus xG. "
                "Positive values mean the player scored more goals than expected. "
                "Negative values mean the player scored fewer goals than expected."
            )

            import plotly.express as px

            if "Goals minus xG" in advanced_metrics.columns:
                xg_chart_df = (
                    advanced_metrics
                    .dropna(subset=["Goals minus xG"])
                    .sort_values("Goals minus xG", ascending=False)
                    .head(20)
                    .copy()
                )

                xg_chart_df["Player Label"] = (
                        xg_chart_df["Player Name"]
                        + " — "
                        + xg_chart_df["Club"]
                )

                xg_chart_df = xg_chart_df.sort_values(
                    "Goals minus xG",
                    ascending=True
                )

                fig_xg = px.bar(
                    xg_chart_df,
                    x="Goals minus xG",
                    y="Player Label",
                    orientation="h",
                    text="Goals minus xG",
                    color="Goals minus xG",
                    title="Top xG Overperformers",
                )

                fig_xg.update_traces(
                    texttemplate="%{text:.2f}",
                    textposition="outside"
                )

                fig_xg.update_layout(
                    xaxis_title="Goals minus expected goals",
                    yaxis_title="Player",
                    height=650,
                    showlegend=False,
                )

                chart_layout(fig_xg, 650)

                st.plotly_chart(fig_xg, width="stretch")
            else:
                st.info("xG columns are not available in this dataset.")
