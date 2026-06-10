import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


def prepare_clustering_data(df):
    """
    Prepare football player data for clustering.
    Adds per-90 metrics where possible.
    """

    cluster_df = df.copy()

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
        if col in cluster_df.columns
    ]

    cluster_df = cluster_df[existing_columns].copy()

    text_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
    ]

    numeric_columns = [
        col for col in cluster_df.columns
        if col not in text_columns
    ]

    for col in numeric_columns:
        cluster_df[col] = pd.to_numeric(
            cluster_df[col],
            errors="coerce"
        )

    if "Minutes Played" not in cluster_df.columns:
        return cluster_df

    cluster_df = cluster_df[
        cluster_df["Minutes Played"].notna()
    ].copy()

    cluster_df = cluster_df[
        cluster_df["Minutes Played"] > 0
    ].copy()

    if "Goals" in cluster_df.columns:
        cluster_df["Goals per 90"] = (
            cluster_df["Goals"] / cluster_df["Minutes Played"] * 90
        )

    if "Assists" in cluster_df.columns:
        cluster_df["Assists per 90"] = (
            cluster_df["Assists"] / cluster_df["Minutes Played"] * 90
        )

    if "Goals" in cluster_df.columns and "Assists" in cluster_df.columns:
        cluster_df["Goals + Assists per 90"] = (
            (cluster_df["Goals"] + cluster_df["Assists"])
            / cluster_df["Minutes Played"]
            * 90
        )

    if "Expected Goals" in cluster_df.columns:
        cluster_df["Expected Goals per 90"] = (
            cluster_df["Expected Goals"] / cluster_df["Minutes Played"] * 90
        )

    if "Expected Assisted Goals" in cluster_df.columns:
        cluster_df["Expected Assisted Goals per 90"] = (
            cluster_df["Expected Assisted Goals"]
            / cluster_df["Minutes Played"]
            * 90
        )

    if (
        "Expected Goals" in cluster_df.columns
        and "Expected Assisted Goals" in cluster_df.columns
    ):
        cluster_df["Expected Goals + Expected Assists per 90"] = (
            (
                cluster_df["Expected Goals"]
                + cluster_df["Expected Assisted Goals"]
            )
            / cluster_df["Minutes Played"]
            * 90
        )

    if "Progressive Carries" in cluster_df.columns:
        cluster_df["Progressive Carries per 90"] = (
            cluster_df["Progressive Carries"]
            / cluster_df["Minutes Played"]
            * 90
        )

    if "Progressive Passes" in cluster_df.columns:
        cluster_df["Progressive Passes per 90"] = (
            cluster_df["Progressive Passes"]
            / cluster_df["Minutes Played"]
            * 90
        )

    if "Progressive Passes Received" in cluster_df.columns:
        cluster_df["Progressive Passes Received per 90"] = (
            cluster_df["Progressive Passes Received"]
            / cluster_df["Minutes Played"]
            * 90
        )

    return cluster_df


def get_available_clustering_features(df):
    """
    Return numeric columns available for clustering.
    """

    cluster_df = prepare_clustering_data(df)

    blocked_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
    ]

    available_features = []

    for col in cluster_df.columns:
        if col in blocked_columns:
            continue

        if pd.api.types.is_numeric_dtype(cluster_df[col]):
            available_features.append(col)

    preferred_order = [
        "Age",
        "Minutes Played",
        "Matches Played",
        "Goals",
        "Assists",
        "Goals + Assists",
        "Goals per 90",
        "Assists per 90",
        "Goals + Assists per 90",
        "Expected Goals",
        "Expected Assisted Goals",
        "Expected Goals per 90",
        "Expected Assisted Goals per 90",
        "Expected Goals + Expected Assists per 90",
        "Progressive Carries",
        "Progressive Passes",
        "Progressive Passes Received",
        "Progressive Carries per 90",
        "Progressive Passes per 90",
        "Progressive Passes Received per 90",
        "Yellow Cards",
        "Red Cards",
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


def cluster_players(
    df,
    selected_features,
    number_of_clusters=4,
    min_minutes=900
):
    """
    Cluster football players using KMeans.
    """

    cluster_df = prepare_clustering_data(df)

    if "Minutes Played" in cluster_df.columns:
        cluster_df = cluster_df[
            cluster_df["Minutes Played"] >= min_minutes
        ].copy()

    selected_features = [
        feature for feature in selected_features
        if feature in cluster_df.columns
    ]

    if len(selected_features) == 0:
        return None, None

    for feature in selected_features:
        cluster_df[feature] = pd.to_numeric(
            cluster_df[feature],
            errors="coerce"
        )

    cluster_df = cluster_df.dropna(subset=selected_features)

    if len(cluster_df) < number_of_clusters:
        return None, None

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(
        cluster_df[selected_features]
    )

    kmeans = KMeans(
        n_clusters=number_of_clusters,
        random_state=42,
        n_init=10
    )

    cluster_df["Cluster"] = kmeans.fit_predict(scaled_features)

    if len(selected_features) >= 2:
        pca = PCA(n_components=2, random_state=42)
        pca_result = pca.fit_transform(scaled_features)

        cluster_df["PCA 1"] = pca_result[:, 0]
        cluster_df["PCA 2"] = pca_result[:, 1]
    else:
        cluster_df["PCA 1"] = scaled_features[:, 0]
        cluster_df["PCA 2"] = 0

    cluster_summary = (
        cluster_df.groupby("Cluster")[selected_features]
        .mean()
        .round(2)
        .reset_index()
    )

    cluster_counts = (
        cluster_df["Cluster"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    cluster_counts.columns = ["Cluster", "Number of Players"]

    cluster_summary = cluster_summary.merge(
        cluster_counts,
        on="Cluster",
        how="left"
    )

    return cluster_df, cluster_summary

def describe_cluster_profiles(cluster_summary, selected_features):
    """
    Create simple human-readable descriptions for every cluster.
    """

    described_summary = cluster_summary.copy()

    feature_means = {}

    for feature in selected_features:
        if feature in described_summary.columns:
            feature_means[feature] = described_summary[feature].mean()

    cluster_names = []
    cluster_descriptions = []

    for _, row in described_summary.iterrows():
        strengths = []
        weaknesses = []

        for feature in selected_features:
            if feature not in described_summary.columns:
                continue

            value = row[feature]
            average_value = feature_means[feature]

            if value > average_value:
                strengths.append(feature)
            elif value < average_value:
                weaknesses.append(feature)

        # Basic cluster naming logic
        if any(feature in strengths for feature in [
            "Goals per 90",
            "Goals + Assists per 90",
            "Expected Goals per 90",
            "Expected Goals + Expected Assists per 90"
        ]):
            cluster_name = "Attacking Players"

        elif any(feature in strengths for feature in [
            "Assists per 90",
            "Expected Assisted Goals per 90",
            "Progressive Passes per 90"
        ]):
            cluster_name = "Creative Players"

        elif any(feature in strengths for feature in [
            "Progressive Carries per 90",
            "Progressive Passes Received per 90"
        ]):
            cluster_name = "Progressive / Ball-Carrying Players"

        elif "Minutes Played" in strengths:
            cluster_name = "Regular Starters"

        elif "Age" in strengths:
            cluster_name = "Experienced Players"

        else:
            cluster_name = "Balanced / Low Output Players"

        if strengths:
            strengths_text = ", ".join(strengths[:4])
        else:
            strengths_text = "no clear above-average metric"

        if weaknesses:
            weaknesses_text = ", ".join(weaknesses[:4])
        else:
            weaknesses_text = "no clear below-average metric"

        description = (
            f"This group is stronger in: {strengths_text}. "
            f"Weaker or lower in: {weaknesses_text}."
        )

        cluster_names.append(cluster_name)
        cluster_descriptions.append(description)

    described_summary["Cluster Profile"] = cluster_names
    described_summary["Description"] = cluster_descriptions

    return described_summary