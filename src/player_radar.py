import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from src.feature_engineering import ordered_numeric_features, prepare_analytics_frame


def prepare_radar_data(df):
    """
    Prepare football player data for radar chart comparison.
    Adds per-90 metrics where possible.
    """

    radar_df = prepare_analytics_frame(df)

    if "Minutes Played" not in radar_df.columns:
        return radar_df

    radar_df = radar_df[
        radar_df["Minutes Played"].notna()
    ].copy()

    radar_df = radar_df[
        radar_df["Minutes Played"] > 0
    ].copy()

    return radar_df


def get_available_radar_features(df):
    """
    Return numeric columns available for radar chart comparison.
    """

    radar_df = prepare_radar_data(df)

    return ordered_numeric_features(radar_df)


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

    identity_column = "Player Name"
    if (
        "Player Record ID" in radar_df.columns
        and any(player in radar_df["Player Record ID"].values for player in selected_players)
    ):
        identity_column = "Player Record ID"

    radar_df = radar_df[
        radar_df[identity_column].isin(selected_players)
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

    existing_base_columns = [
        col for col in [
            "Player Record ID",
            "Player Selection Label",
            "Player Name",
            "Nationality",
            "Position",
            "Primary Position",
            "Club",
            "League",
            "Age",
            "Minutes Played",
            "Goals",
            "Assists",
        ]
        if col in radar_df.columns
    ]

    radar_normalized_df = radar_df[existing_base_columns].copy()

    for feature in selected_features:
        radar_normalized_df[feature] = normalized_df[feature].round(1)

    original_values_df = radar_df.copy()

    return radar_normalized_df, original_values_df
