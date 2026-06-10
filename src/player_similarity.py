import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity


def prepare_similarity_data(df):
    """
    Prepare football player data for similarity comparison.
    Adds per-90 metrics if they are not already in the dataframe.
    """

    similarity_df = df.copy()

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
        if col in similarity_df.columns
    ]

    similarity_df = similarity_df[existing_columns].copy()

    numeric_columns = [
        col for col in similarity_df.columns
        if col not in [
            "Player Name",
            "Nationality",
            "Position",
            "Club",
            "League",
        ]
    ]

    for col in numeric_columns:
        similarity_df[col] = pd.to_numeric(
            similarity_df[col],
            errors="coerce"
        )

    if "Minutes Played" not in similarity_df.columns:
        return similarity_df

    similarity_df = similarity_df[
        similarity_df["Minutes Played"].notna()
    ].copy()

    similarity_df = similarity_df[
        similarity_df["Minutes Played"] > 0
    ].copy()

    if "Goals" in similarity_df.columns:
        similarity_df["Goals per 90"] = (
            similarity_df["Goals"] / similarity_df["Minutes Played"] * 90
        )

    if "Assists" in similarity_df.columns:
        similarity_df["Assists per 90"] = (
            similarity_df["Assists"] / similarity_df["Minutes Played"] * 90
        )

    if "Goals" in similarity_df.columns and "Assists" in similarity_df.columns:
        similarity_df["Goals + Assists per 90"] = (
            (similarity_df["Goals"] + similarity_df["Assists"])
            / similarity_df["Minutes Played"]
            * 90
        )

    if "Expected Goals" in similarity_df.columns:
        similarity_df["Expected Goals per 90"] = (
            similarity_df["Expected Goals"] / similarity_df["Minutes Played"] * 90
        )

    if "Expected Assisted Goals" in similarity_df.columns:
        similarity_df["Expected Assisted Goals per 90"] = (
            similarity_df["Expected Assisted Goals"]
            / similarity_df["Minutes Played"]
            * 90
        )

    if (
        "Expected Goals" in similarity_df.columns
        and "Expected Assisted Goals" in similarity_df.columns
    ):
        similarity_df["Expected Goals + Expected Assists per 90"] = (
            (
                similarity_df["Expected Goals"]
                + similarity_df["Expected Assisted Goals"]
            )
            / similarity_df["Minutes Played"]
            * 90
        )

    if "Progressive Carries" in similarity_df.columns:
        similarity_df["Progressive Carries per 90"] = (
            similarity_df["Progressive Carries"]
            / similarity_df["Minutes Played"]
            * 90
        )

    if "Progressive Passes" in similarity_df.columns:
        similarity_df["Progressive Passes per 90"] = (
            similarity_df["Progressive Passes"]
            / similarity_df["Minutes Played"]
            * 90
        )

    if "Progressive Passes Received" in similarity_df.columns:
        similarity_df["Progressive Passes Received per 90"] = (
            similarity_df["Progressive Passes Received"]
            / similarity_df["Minutes Played"]
            * 90
        )

    return similarity_df


def get_available_similarity_features(df):
    """
    Return numeric columns that can be used for player similarity.
    """

    prepared_df = prepare_similarity_data(df)

    blocked_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
    ]

    available_features = []

    for col in prepared_df.columns:
        if col in blocked_columns:
            continue

        if pd.api.types.is_numeric_dtype(prepared_df[col]):
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


def find_similar_players(
    df,
    selected_player,
    selected_features,
    top_n=10,
    min_minutes=900,
    same_position_only=True
):
    """
    Find players most similar to the selected player using cosine similarity.
    The user decides which numeric features are used.
    """

    similarity_df = prepare_similarity_data(df)

    if "Minutes Played" in similarity_df.columns:
        similarity_df = similarity_df[
            similarity_df["Minutes Played"] >= min_minutes
        ].copy()

    selected_player_row = similarity_df[
        similarity_df["Player Name"] == selected_player
    ]

    if selected_player_row.empty:
        return None

    if same_position_only:
        selected_position = selected_player_row["Position"].iloc[0]

        similarity_df = similarity_df[
            similarity_df["Position"] == selected_position
        ].copy()

    if selected_player not in similarity_df["Player Name"].values:
        return None

    selected_features = [
        feature for feature in selected_features
        if feature in similarity_df.columns
    ]

    if len(selected_features) == 0:
        return None

    for feature in selected_features:
        similarity_df[feature] = pd.to_numeric(
            similarity_df[feature],
            errors="coerce"
        )

    similarity_df = similarity_df.dropna(subset=selected_features)

    if len(similarity_df) < 2:
        return None

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(
        similarity_df[selected_features]
    )

    similarity_matrix = cosine_similarity(scaled_features)

    player_index = similarity_df[
        similarity_df["Player Name"] == selected_player
    ].index[0]

    player_position = similarity_df.index.get_loc(player_index)

    similarity_scores = list(enumerate(similarity_matrix[player_position]))

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    similar_players = similarity_scores[1:top_n + 1]

    result_indices = [i[0] for i in similar_players]
    result_scores = [i[1] for i in similar_players]

    result_df = similarity_df.iloc[result_indices].copy()
    result_df["Similarity Score"] = result_scores
    result_df["Similarity Score"] = result_df["Similarity Score"].round(3)

    result_df = result_df.sort_values(
        "Similarity Score",
        ascending=False
    )

    return result_df