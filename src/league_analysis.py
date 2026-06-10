import pandas as pd


def prepare_league_analysis_data(df):
    """
    Prepare league-level summary data.
    """

    league_df = df.copy()

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
        "Yellow Cards",
        "Red Cards",
        "Minutes Played",
        "Matches Played",
    ]

    possible_mean_columns = [
        "Age",
        "Goals per 90",
        "Assists per 90",
        "Goals + Assists per 90",
        "Expected Goals per 90",
        "Expected Assisted Goals per 90",
    ]

    for col in possible_sum_columns:
        if col in league_df.columns:
            aggregation[col] = "sum"

    for col in possible_mean_columns:
        if col in league_df.columns:
            aggregation[col] = "mean"

    if "Player Name" in league_df.columns:
        aggregation["Player Name"] = "nunique"

    if "Club" in league_df.columns:
        aggregation["Club"] = "nunique"

    league_summary = (
        league_df.groupby("League", as_index=False)
        .agg(aggregation)
    )

    rename_columns = {
        "Player Name": "Players",
        "Club": "Clubs",
        "Age": "Average Age",
        "Minutes Played": "Total Minutes",
        "Matches Played": "Total Matches Played",
    }

    league_summary = league_summary.rename(columns=rename_columns)

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

    position_summary = (
        league_df.groupby(["League", "Position"], as_index=False)
        .agg({"Player Name": "nunique"})
        .rename(columns={"Player Name": "Number of Players"})
        .sort_values("Number of Players", ascending=False)
    )

    return position_summary