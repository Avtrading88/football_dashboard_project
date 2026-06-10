import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def prepare_radar_data(df):
    """
    Prepare football player data for radar chart comparison.
    Adds per-90 metrics where possible.
    """

    radar_df = df.copy()

    useful_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
        "Age",
        "Minutes Played",
        "Matches Played",
        "Goals",
        "Assists",
        "Goals + Assists",
        "Expected Goals",
        "Expected Assisted Goals",
        "Non-Penalty Expected Goals",
        "Non-Penalty xG + Expected Assists",
        "Progressive Carries",
        "Progressive Passes",
        "Progressive Passes Received",
        "Yellow Cards",
        "Red Cards",
    ]

    existing_columns = [
        col for col in useful_columns
        if col in radar_df.columns
    ]

    radar_df = radar_df[existing_columns].copy()

    text_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
    ]

    numeric_columns = [
        col for col in radar_df.columns
        if col not in text_columns
    ]

    for col in numeric_columns:
        radar_df[col] = pd.to_numeric(
            radar_df[col],
            errors="coerce"
        )

    if "Minutes Played" not in radar_df.columns:
        return radar_df

    radar_df = radar_df[
        radar_df["Minutes Played"].notna()
    ].copy()

    radar_df = radar_df[
        radar_df["Minutes Played"] > 0
    ].copy()

    if "Goals" in radar_df.columns:
        radar_df["Goals per 90"] = (
            radar_df["Goals"] / radar_df["Minutes Played"] * 90
        )

    if "Assists" in radar_df.columns:
        radar_df["Assists per 90"] = (
            radar_df["Assists"] / radar_df["Minutes Played"] * 90
        )

    if "Goals" in radar_df.columns and "Assists" in radar_df.columns:
        radar_df["Goals + Assists per 90"] = (
            (radar_df["Goals"] + radar_df["Assists"])
            / radar_df["Minutes Played"]
            * 90
        )

    if "Expected Goals" in radar_df.columns:
        radar_df["Expected Goals per 90"] = (
            radar_df["Expected Goals"] / radar_df["Minutes Played"] * 90
        )

    if "Expected Assisted Goals" in radar_df.columns:
        radar_df["Expected Assisted Goals per 90"] = (
            radar_df["Expected Assisted Goals"]
            / radar_df["Minutes Played"]
            * 90
        )

    if (
        "Expected Goals" in radar_df.columns
        and "Expected Assisted Goals" in radar_df.columns
    ):
        radar_df["Expected Goals + Expected Assists per 90"] = (
            (
                radar_df["Expected Goals"]
                + radar_df["Expected Assisted Goals"]
            )
            / radar_df["Minutes Played"]
            * 90
        )

    if "Progressive Carries" in radar_df.columns:
        radar_df["Progressive Carries per 90"] = (
            radar_df["Progressive Carries"]
            / radar_df["Minutes Played"]
            * 90
        )

    if "Progressive Passes" in radar_df.columns:
        radar_df["Progressive Passes per 90"] = (
            radar_df["Progressive Passes"]
            / radar_df["Minutes Played"]
            * 90
        )

    if "Progressive Passes Received" in radar_df.columns:
        radar_df["Progressive Passes Received per 90"] = (
            radar_df["Progressive Passes Received"]
            / radar_df["Minutes Played"]
            * 90
        )

    return radar_df


def get_available_radar_features(df):
    """
    Return numeric columns available for radar chart comparison.
    """

    radar_df = prepare_radar_data(df)

    blocked_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
    ]

    available_features = []

    for col in radar_df.columns:
        if col in blocked_columns:
            continue

        if pd.api.types.is_numeric_dtype(radar_df[col]):
            available_features.append(col)

    preferred_order = [
        "Goals per 90",
        "Assists per 90",
        "Goals + Assists per 90",
        "Expected Goals per 90",
        "Expected Assisted Goals per 90",
        "Expected Goals + Expected Assists per 90",
        "Progressive Carries per 90",
        "Progressive Passes per 90",
        "Progressive Passes Received per 90",
        "Goals",
        "Assists",
        "Expected Goals",
        "Expected Assisted Goals",
        "Progressive Carries",
        "Progressive Passes",
        "Progressive Passes Received",
        "Age",
        "Minutes Played",
        "Matches Played",
    ]

    ordered_features = [
        col for col in preferred_order
        if col in available_features
    ]

    remaining_features = [
        col for col in available_features
        if col not in ordered_features
    ]

    return ordered_features + remaining_features


def create_radar_comparison_data(
    df,
    selected_players,
    selected_features,
    min_minutes=0
):
    """
    Create normalized radar chart data.
    Values are scaled from 0 to 100 so different statistics can be compared.
    """

    radar_df = prepare_radar_data(df)

    if "Minutes Played" in radar_df.columns:
        radar_df = radar_df[
            radar_df["Minutes Played"] >= min_minutes
        ].copy()

    radar_df = radar_df[
        radar_df["Player Name"].isin(selected_players)
    ].copy()

    selected_features = [
        feature for feature in selected_features
        if feature in radar_df.columns
    ]

    if radar_df.empty or len(selected_features) == 0:
        return None, None

    for feature in selected_features:
        radar_df[feature] = pd.to_numeric(
            radar_df[feature],
            errors="coerce"
        )

    radar_df = radar_df.dropna(subset=selected_features)

    if radar_df.empty:
        return None, None

    # Use all available filtered data for fair scaling, not only selected players.
    scaling_df = prepare_radar_data(df)

    if "Minutes Played" in scaling_df.columns:
        scaling_df = scaling_df[
            scaling_df["Minutes Played"] >= min_minutes
        ].copy()

    scaling_df = scaling_df.dropna(subset=selected_features)

    if scaling_df.empty:
        return None, None

    scaler = MinMaxScaler(feature_range=(0, 100))
    scaler.fit(scaling_df[selected_features])

    normalized_values = scaler.transform(radar_df[selected_features])

    normalized_df = pd.DataFrame(
        normalized_values,
        columns=selected_features,
        index=radar_df.index
    )

    radar_normalized_df = radar_df[
        [
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
    ].copy()

    existing_base_columns = [
        col for col in radar_normalized_df.columns
        if col in radar_df.columns
    ]

    radar_normalized_df = radar_df[existing_base_columns].copy()

    for feature in selected_features:
        radar_normalized_df[feature] = normalized_df[feature].round(1)

    original_values_df = radar_df.copy()

    return radar_normalized_df, original_values_df