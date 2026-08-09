import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from src.feature_engineering import prepare_analytics_frame


ROLE_SCORE_PROFILES = {
    "FW": [
        ("Non-Penalty Goals per 90", 28, False),
        ("Assists per 90", 16, False),
        ("Shots on Target per 90", 20, False),
        ("Shot Accuracy Percentage", 12, False),
        ("Goal Conversion Percentage", 14, False),
        ("Fouled per 90", 10, False),
    ],
    "MF": [
        ("Goals + Assists per 90", 22, False),
        ("Assists per 90", 14, False),
        ("Crosses per 90", 18, False),
        ("Defensive Actions per 90", 24, False),
        ("Fouled per 90", 12, False),
        ("Shot Accuracy Percentage", 10, False),
    ],
    "DF": [
        ("Defensive Actions per 90", 40, False),
        ("Tackles Won per 90", 15, False),
        ("Interceptions per 90", 15, False),
        ("Fouls Committed per 90", 10, True),
        ("Yellow Cards per 90", 10, True),
        ("Crosses per 90", 10, False),
    ],
    "GK": [
        ("Save Percentage", 45, False),
        ("Clean Sheet Percentage", 25, False),
        ("Goals Against per 90", 20, True),
        ("Penalty Save Percentage", 10, False),
    ],
}


def prepare_scouting_data(df):
    """
    Prepare player data for scoring and young talent detection.
    Adds per-90 metrics and normalized score columns.
    """

    scouting_df = prepare_analytics_frame(df)

    if "Minutes Played" not in scouting_df.columns:
        return scouting_df

    scouting_df = scouting_df[
        scouting_df["Minutes Played"].notna()
    ].copy()

    scouting_df = scouting_df[
        scouting_df["Minutes Played"] > 0
    ].copy()

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

    requested_weight = goal_weight + assist_weight + xg_weight + progression_weight
    weighted_components = []
    active_weight = 0
    active_component_names = []

    component_definitions = [
        ("Goals per 90 Score", goal_weight, "goals"),
        ("Assists per 90 Score", assist_weight, "assists"),
        (
            "Expected Goals + Expected Assists per 90 Score",
            xg_weight,
            "expected output",
        ),
    ]

    for score_column, weight, component_name in component_definitions:
        if score_column in normalized_columns and weight > 0:
            weighted_components.append(scoring_df[score_column] * weight)
            active_weight += weight
            active_component_names.append(component_name)

    progression_columns = [
        column
        for column in [
            "Progressive Carries per 90 Score",
            "Progressive Passes per 90 Score",
        ]
        if column in normalized_columns
    ]
    if progression_columns and progression_weight > 0:
        progression_score = scoring_df[progression_columns].mean(axis=1)
        weighted_components.append(progression_score * progression_weight)
        active_weight += progression_weight
        active_component_names.append("progression")

    if active_weight == 0:
        return None

    total_component = weighted_components[0].copy()
    for component in weighted_components[1:]:
        total_component = total_component + component

    scoring_df["Player Score"] = total_component / active_weight
    scoring_df["Score Coverage %"] = round(
        active_weight / requested_weight * 100,
        1,
    ) if requested_weight > 0 else 100.0
    scoring_df["Score Components Used"] = ", ".join(active_component_names)

    scoring_df["Player Score"] = scoring_df["Player Score"].round(1)

    scoring_df = scoring_df.sort_values(
        "Player Score",
        ascending=False
    )

    return scoring_df


def calculate_role_percentile_scores(df, min_minutes=900):
    """Rank players against peers in the same primary position.

    Percentiles are more robust and understandable than comparing defenders,
    midfielders, forwards and goalkeepers with one universal formula. Missing
    row-level metrics reduce coverage but do not silently count as zero.
    """

    scoring_df = prepare_scouting_data(df)
    required_columns = {"Primary Position", "Minutes Played"}
    if not required_columns.issubset(scoring_df.columns):
        return None

    scoring_df = scoring_df[
        scoring_df["Minutes Played"] >= min_minutes
    ].copy()
    scoring_df = scoring_df[
        scoring_df["Primary Position"].isin(ROLE_SCORE_PROFILES)
    ].copy()

    if scoring_df.empty:
        return None

    role_results = []

    for role, profile in ROLE_SCORE_PROFILES.items():
        cohort = scoring_df[scoring_df["Primary Position"] == role].copy()
        if cohort.empty:
            continue

        weighted_total = pd.Series(0.0, index=cohort.index)
        available_weight = pd.Series(0.0, index=cohort.index)
        profile_weight = sum(weight for _, weight, _ in profile)
        metrics_used = []

        for metric, weight, lower_is_better in profile:
            if metric not in cohort.columns:
                continue

            numeric_metric = pd.to_numeric(cohort[metric], errors="coerce")
            valid = numeric_metric.notna()
            if not valid.any():
                continue

            percentile = numeric_metric.rank(pct=True, method="average") * 100
            if lower_is_better:
                percentile = 100 - percentile

            percentile_column = f"{metric} Percentile"
            cohort[percentile_column] = percentile.round(1)
            weighted_total = weighted_total.add(percentile.fillna(0) * weight)
            available_weight = available_weight.add(valid.astype(float) * weight)
            metrics_used.append(metric)

        valid_rows = available_weight > 0
        cohort = cohort[valid_rows].copy()
        if cohort.empty:
            continue

        cohort["Role Score"] = (
            weighted_total[valid_rows] / available_weight[valid_rows]
        ).round(1)
        cohort["Role Score Coverage %"] = (
            available_weight[valid_rows] / profile_weight * 100
        ).round(1)
        cohort["Role Metrics Used"] = ", ".join(metrics_used)
        cohort["Role Cohort Size"] = len(cohort)
        cohort["Role Rank"] = (
            cohort["Role Score"].rank(method="min", ascending=False).astype(int)
        )
        role_results.append(cohort)

    if not role_results:
        return None

    return (
        pd.concat(role_results, ignore_index=True)
        .sort_values(["Primary Position", "Role Score"], ascending=[True, False])
    )


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
