import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

from src.feature_engineering import ordered_numeric_features, prepare_analytics_frame


def prepare_similarity_data(df):
    """
    Prepare football player data for similarity comparison.
    Adds per-90 metrics if they are not already in the dataframe.
    """

    similarity_df = prepare_analytics_frame(df)

    if "Minutes Played" not in similarity_df.columns:
        return similarity_df

    similarity_df = similarity_df[
        similarity_df["Minutes Played"].notna()
    ].copy()

    similarity_df = similarity_df[
        similarity_df["Minutes Played"] > 0
    ].copy()

    return similarity_df


def get_available_similarity_features(df):
    """
    Return numeric columns that can be used for player similarity.
    """

    prepared_df = prepare_similarity_data(df)

    return ordered_numeric_features(prepared_df)


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

    identity_column = (
        "Player Record ID"
        if "Player Record ID" in similarity_df.columns
        and selected_player in similarity_df["Player Record ID"].values
        else "Player Name"
    )

    selected_player_row = similarity_df[
        similarity_df[identity_column] == selected_player
    ]

    if selected_player_row.empty:
        return None

    if same_position_only:
        position_column = (
            "Primary Position"
            if "Primary Position" in similarity_df.columns
            else "Position"
        )
        selected_position = selected_player_row[position_column].iloc[0]

        similarity_df = similarity_df[
            similarity_df[position_column] == selected_position
        ].copy()

    if selected_player not in similarity_df[identity_column].values:
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
        similarity_df[identity_column] == selected_player
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
