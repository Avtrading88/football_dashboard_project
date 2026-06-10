import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def prepare_scouting_data(df):
    """
    Prepare player data for scoring and young talent detection.
    Adds per-90 metrics and normalized score columns.
    """

    scouting_df = df.copy()

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
        "Progressive Carries",
        "Progressive Passes",
        "Progressive Passes Received",
        "Yellow Cards",
        "Red Cards",
    ]

    existing_columns = [
        col for col in useful_columns
        if col in scouting_df.columns
    ]

    scouting_df = scouting_df[existing_columns].copy()

    text_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
    ]

    numeric_columns = [
        col for col in scouting_df.columns
        if col not in text_columns
    ]

    for col in numeric_columns:
        scouting_df[col] = pd.to_numeric(
            scouting_df[col],
            errors="coerce"
        )

    if "Minutes Played" not in scouting_df.columns:
        return scouting_df

    scouting_df = scouting_df[
        scouting_df["Minutes Played"].notna()
    ].copy()

    scouting_df = scouting_df[
        scouting_df["Minutes Played"] > 0
    ].copy()

    if "Goals" in scouting_df.columns:
        scouting_df["Goals per 90"] = (
            scouting_df["Goals"] / scouting_df["Minutes Played"] * 90
        )

    if "Assists" in scouting_df.columns:
        scouting_df["Assists per 90"] = (
            scouting_df["Assists"] / scouting_df["Minutes Played"] * 90
        )

    if "Goals" in scouting_df.columns and "Assists" in scouting_df.columns:
        scouting_df["Goals + Assists per 90"] = (
            (scouting_df["Goals"] + scouting_df["Assists"])
            / scouting_df["Minutes Played"]
            * 90
        )

    if "Expected Goals" in scouting_df.columns:
        scouting_df["Expected Goals per 90"] = (
            scouting_df["Expected Goals"] / scouting_df["Minutes Played"] * 90
        )

    if "Expected Assisted Goals" in scouting_df.columns:
        scouting_df["Expected Assisted Goals per 90"] = (
            scouting_df["Expected Assisted Goals"]
            / scouting_df["Minutes Played"]
            * 90
        )

    if (
        "Expected Goals" in scouting_df.columns
        and "Expected Assisted Goals" in scouting_df.columns
    ):
        scouting_df["Expected Goals + Expected Assists per 90"] = (
            (
                scouting_df["Expected Goals"]
                + scouting_df["Expected Assisted Goals"]
            )
            / scouting_df["Minutes Played"]
            * 90
        )

    if "Progressive Carries" in scouting_df.columns:
        scouting_df["Progressive Carries per 90"] = (
            scouting_df["Progressive Carries"]
            / scouting_df["Minutes Played"]
            * 90
        )

    if "Progressive Passes" in scouting_df.columns:
        scouting_df["Progressive Passes per 90"] = (
            scouting_df["Progressive Passes"]
            / scouting_df["Minutes Played"]
            * 90
        )

    if "Progressive Passes Received" in scouting_df.columns:
        scouting_df["Progressive Passes Received per 90"] = (
            scouting_df["Progressive Passes Received"]
            / scouting_df["Minutes Played"]
            * 90
        )

    return scouting_df


def add_normalized_columns(df, score_features):
    """
    Normalize selected score features from 0 to 100.
    """

    scoring_df = df.copy()

    available_features = [
        feature for feature in score_features
        if feature in scoring_df.columns
    ]

    scoring_df = scoring_df.dropna(subset=available_features).copy()

    if scoring_df.empty or len(available_features) == 0:
        return scoring_df, []

    scaler = MinMaxScaler(feature_range=(0, 100))

    normalized_values = scaler.fit_transform(
        scoring_df[available_features]
    )

    normalized_columns = []

    for i, feature in enumerate(available_features):
        normalized_col = f"{feature} Score"
        scoring_df[normalized_col] = normalized_values[:, i]
        normalized_columns.append(normalized_col)

    return scoring_df, normalized_columns


def calculate_player_scores(
    df,
    min_minutes=900,
    goal_weight=35,
    assist_weight=25,
    xg_weight=20,
    progression_weight=20
):
    """
    Calculate general player performance score.
    """

    scoring_df = prepare_scouting_data(df)

    if "Minutes Played" in scoring_df.columns:
        scoring_df = scoring_df[
            scoring_df["Minutes Played"] >= min_minutes
        ].copy()

    score_features = [
        "Goals per 90",
        "Assists per 90",
        "Expected Goals + Expected Assists per 90",
        "Progressive Carries per 90",
        "Progressive Passes per 90",
    ]

    scoring_df, normalized_columns = add_normalized_columns(
        scoring_df,
        score_features
    )

    if scoring_df.empty:
        return None

    # Create missing score columns as 0 if the dataset does not have some metrics.
    required_score_columns = {
        "Goals per 90 Score": 0,
        "Assists per 90 Score": 0,
        "Expected Goals + Expected Assists per 90 Score": 0,
        "Progressive Carries per 90 Score": 0,
        "Progressive Passes per 90 Score": 0,
    }

    for col, default_value in required_score_columns.items():
        if col not in scoring_df.columns:
            scoring_df[col] = default_value

    total_weight = goal_weight + assist_weight + xg_weight + progression_weight

    if total_weight == 0:
        total_weight = 1

    progression_score = (
        scoring_df["Progressive Carries per 90 Score"]
        + scoring_df["Progressive Passes per 90 Score"]
    ) / 2

    scoring_df["Player Score"] = (
        scoring_df["Goals per 90 Score"] * goal_weight
        + scoring_df["Assists per 90 Score"] * assist_weight
        + scoring_df["Expected Goals + Expected Assists per 90 Score"] * xg_weight
        + progression_score * progression_weight
    ) / total_weight

    scoring_df["Player Score"] = scoring_df["Player Score"].round(1)

    scoring_df = scoring_df.sort_values(
        "Player Score",
        ascending=False
    )

    return scoring_df


def calculate_young_talent_scores(
    df,
    max_age=23,
    min_minutes=500,
    performance_weight=60,
    age_weight=25,
    minutes_weight=15
):
    """
    Calculate young talent score.
    Younger players with strong output and enough minutes rank higher.
    """

    talent_df = calculate_player_scores(
        df=df,
        min_minutes=min_minutes
    )

    if talent_df is None or talent_df.empty:
        return None

    if "Age" not in talent_df.columns:
        return None

    talent_df = talent_df[
        talent_df["Age"] <= max_age
    ].copy()

    if talent_df.empty:
        return None

    score_features = [
        "Player Score",
        "Minutes Played",
    ]

    talent_df, normalized_columns = add_normalized_columns(
        talent_df,
        score_features
    )

    if talent_df.empty:
        return None

    # Younger age should be better, so reverse the age score.
    age_min = talent_df["Age"].min()
    age_max = talent_df["Age"].max()

    if age_max == age_min:
        talent_df["Age Potential Score"] = 100
    else:
        talent_df["Age Potential Score"] = (
            (age_max - talent_df["Age"])
            / (age_max - age_min)
            * 100
        )

    if "Player Score Score" not in talent_df.columns:
        talent_df["Player Score Score"] = 0

    if "Minutes Played Score" not in talent_df.columns:
        talent_df["Minutes Played Score"] = 0

    total_weight = performance_weight + age_weight + minutes_weight

    if total_weight == 0:
        total_weight = 1

    talent_df["Young Talent Score"] = (
        talent_df["Player Score Score"] * performance_weight
        + talent_df["Age Potential Score"] * age_weight
        + talent_df["Minutes Played Score"] * minutes_weight
    ) / total_weight

    talent_df["Young Talent Score"] = talent_df["Young Talent Score"].round(1)

    talent_df = talent_df.sort_values(
        "Young Talent Score",
        ascending=False
    )

    return talent_df