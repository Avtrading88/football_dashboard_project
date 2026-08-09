import pandas as pd

from src.feature_engineering import prepare_analytics_frame


def prepare_league_analysis_data(df):
    """
    Prepare league-level summary data.
    """

    league_df = prepare_analytics_frame(df)

    numeric_columns = [
        "Age",
        "Minutes Played",
        "Matches Played",
        "Goals",
        "Assists",
        "Expected Goals",
        "Expected Assisted Goals",
        "Progressive Carries",
        "Progressive Passes",
        "Shots",
        "Shots on Target",
        "Crosses",
        "Tackles Won",
        "Interceptions",
        "Fouled",
        "Fouls Committed",
        "Saves",
        "Shots on Target Against",
        "Yellow Cards",
        "Red Cards",
    ]

    for col in numeric_columns:
        if col in league_df.columns:
            league_df[col] = pd.to_numeric(
                league_df[col],
                errors="coerce"
            )

    if "Minutes Played" in league_df.columns:
        league_df = league_df[
            league_df["Minutes Played"].fillna(0) > 0
        ].copy()

    if "Goals" in league_df.columns and "Minutes Played" in league_df.columns:
        league_df["Goals per 90"] = (
            league_df["Goals"] / league_df["Minutes Played"] * 90
        )

    if "Assists" in league_df.columns and "Minutes Played" in league_df.columns:
        league_df["Assists per 90"] = (
            league_df["Assists"] / league_df["Minutes Played"] * 90
        )

    if (
        "Goals" in league_df.columns
        and "Assists" in league_df.columns
        and "Minutes Played" in league_df.columns
    ):
        league_df["Goals + Assists per 90"] = (
            (league_df["Goals"] + league_df["Assists"])
            / league_df["Minutes Played"]
            * 90
        )

    if "Expected Goals" in league_df.columns and "Minutes Played" in league_df.columns:
        league_df["Expected Goals per 90"] = (
            league_df["Expected Goals"] / league_df["Minutes Played"] * 90
        )

    if "Expected Assisted Goals" in league_df.columns and "Minutes Played" in league_df.columns:
        league_df["Expected Assisted Goals per 90"] = (
            league_df["Expected Assisted Goals"] / league_df["Minutes Played"] * 90
        )

    return league_df


def create_league_summary(df):
    """
    Create league comparison table.
    """

    league_df = prepare_league_analysis_data(df)

    aggregation = {}

    possible_sum_columns = [
        "Goals",
        "Assists",
        "Expected Goals",
        "Expected Assisted Goals",
        "Progressive Carries",
        "Progressive Passes",
        "Shots",
        "Shots on Target",
        "Crosses",
        "Tackles Won",
        "Interceptions",
        "Defensive Actions",
        "Fouled",
        "Fouls Committed",
        "Saves",
        "Shots on Target Against",
        "Clean Sheets",
        "Yellow Cards",
        "Red Cards",
        "Minutes Played",
        "Matches Played",
    ]

    possible_mean_columns = ["Age"]

    for col in possible_sum_columns:
        if col in league_df.columns:
            aggregation[col] = "sum"

    for col in possible_mean_columns:
        if col in league_df.columns:
            aggregation[col] = "mean"

    player_identity_column = (
        "Player ID" if "Player ID" in league_df.columns else "Player Name"
    )
    if player_identity_column in league_df.columns:
        aggregation[player_identity_column] = "nunique"

    if "Club" in league_df.columns:
        aggregation["Club"] = "nunique"

    league_summary = (
        league_df.groupby("League", as_index=False)
        .agg(aggregation)
    )

    rename_columns = {
        player_identity_column: "Players",
        "Club": "Clubs",
        "Age": "Average Age",
        "Minutes Played": "Total Minutes",
        "Matches Played": "Player Appearances",
    }

    league_summary = league_summary.rename(columns=rename_columns)

    if "Total Minutes" in league_summary.columns:
        denominator = league_summary["Total Minutes"].replace(0, pd.NA)
        rate_sources = {
            "Goals": "Goals per 90",
            "Assists": "Assists per 90",
            "Expected Goals": "Expected Goals per 90",
            "Expected Assisted Goals": "Expected Assisted Goals per 90",
            "Shots": "Shots per 90",
            "Shots on Target": "Shots on Target per 90",
            "Crosses": "Crosses per 90",
            "Tackles Won": "Tackles Won per 90",
            "Interceptions": "Interceptions per 90",
            "Defensive Actions": "Defensive Actions per 90",
            "Fouled": "Fouled per 90",
            "Fouls Committed": "Fouls Committed per 90",
        }
        for source, target in rate_sources.items():
            if source in league_summary.columns:
                league_summary[target] = league_summary[source] / denominator * 90

    if {"Goals", "Assists", "Total Minutes"}.issubset(league_summary.columns):
        league_summary["Goals + Assists per 90"] = (
            (league_summary["Goals"] + league_summary["Assists"])
            / league_summary["Total Minutes"].replace(0, pd.NA)
            * 90
        )

    if {"Saves", "Shots on Target Against"}.issubset(league_summary.columns):
        league_summary["Save Percentage"] = (
            league_summary["Saves"]
            / league_summary["Shots on Target Against"].replace(0, pd.NA)
            * 100
        )

    numeric_cols = league_summary.select_dtypes(include="number").columns

    league_summary[numeric_cols] = league_summary[numeric_cols].round(2)

    if "Goals" in league_summary.columns:
        league_summary = league_summary.sort_values(
            "Goals",
            ascending=False
        )

    return league_summary


def create_league_position_summary(df):
    """
    Count players by league and position.
    """

    league_df = df.copy()

    if "League" not in league_df.columns or "Position" not in league_df.columns:
        return None

    player_identity_column = (
        "Player ID" if "Player ID" in league_df.columns else "Player Name"
    )

    position_summary = (
        league_df.groupby(["League", "Position"], as_index=False)
        .agg({player_identity_column: "nunique"})
        .rename(columns={player_identity_column: "Number of Players"})
        .sort_values("Number of Players", ascending=False)
    )

    return position_summary
