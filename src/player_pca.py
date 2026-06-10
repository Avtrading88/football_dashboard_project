import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA


def prepare_pca_data(df):
    """
    Prepare player data for PCA profile visualization.
    """

    pca_df = df.copy()

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
        if col in pca_df.columns
    ]

    pca_df = pca_df[existing_columns].copy()

    text_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
    ]

    numeric_columns = [
        col for col in pca_df.columns
        if col not in text_columns
    ]

    for col in numeric_columns:
        pca_df[col] = pd.to_numeric(
            pca_df[col],
            errors="coerce"
        )

    if "Minutes Played" not in pca_df.columns:
        return pca_df

    pca_df = pca_df[
        pca_df["Minutes Played"].notna()
    ].copy()

    pca_df = pca_df[
        pca_df["Minutes Played"] > 0
    ].copy()

    if "Goals" in pca_df.columns:
        pca_df["Goals per 90"] = (
            pca_df["Goals"] / pca_df["Minutes Played"] * 90
        )

    if "Assists" in pca_df.columns:
        pca_df["Assists per 90"] = (
            pca_df["Assists"] / pca_df["Minutes Played"] * 90
        )

    if "Goals" in pca_df.columns and "Assists" in pca_df.columns:
        pca_df["Goals + Assists per 90"] = (
            (pca_df["Goals"] + pca_df["Assists"])
            / pca_df["Minutes Played"]
            * 90
        )

    if "Expected Goals" in pca_df.columns:
        pca_df["Expected Goals per 90"] = (
            pca_df["Expected Goals"] / pca_df["Minutes Played"] * 90
        )

    if "Expected Assisted Goals" in pca_df.columns:
        pca_df["Expected Assisted Goals per 90"] = (
            pca_df["Expected Assisted Goals"]
            / pca_df["Minutes Played"]
            * 90
        )

    if (
        "Expected Goals" in pca_df.columns
        and "Expected Assisted Goals" in pca_df.columns
    ):
        pca_df["Expected Goals + Expected Assists per 90"] = (
            (
                pca_df["Expected Goals"]
                + pca_df["Expected Assisted Goals"]
            )
            / pca_df["Minutes Played"]
            * 90
        )

    if "Progressive Carries" in pca_df.columns:
        pca_df["Progressive Carries per 90"] = (
            pca_df["Progressive Carries"]
            / pca_df["Minutes Played"] * 90
        )

    if "Progressive Passes" in pca_df.columns:
        pca_df["Progressive Passes per 90"] = (
            pca_df["Progressive Passes"]
            / pca_df["Minutes Played"] * 90
        )

    if "Progressive Passes Received" in pca_df.columns:
        pca_df["Progressive Passes Received per 90"] = (
            pca_df["Progressive Passes Received"]
            / pca_df["Minutes Played"] * 90
        )

    return pca_df


def get_available_pca_features(df):
    """
    Return numeric columns available for PCA.
    """

    pca_df = prepare_pca_data(df)

    blocked_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
    ]

    available_features = []

    for col in pca_df.columns:
        if col in blocked_columns:
            continue

        if pd.api.types.is_numeric_dtype(pca_df[col]):
            available_features.append(col)

    preferred_order = [
        "Age",
        "Minutes Played",
        "Matches Played",
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


def create_player_pca(
    df,
    selected_features,
    min_minutes=900
):
    """
    Create PCA data for player profile visualization.
    """

    pca_df = prepare_pca_data(df)

    if "Minutes Played" in pca_df.columns:
        pca_df = pca_df[
            pca_df["Minutes Played"] >= min_minutes
        ].copy()

    selected_features = [
        feature for feature in selected_features
        if feature in pca_df.columns
    ]

    if len(selected_features) < 2:
        return None, None, None

    for feature in selected_features:
        pca_df[feature] = pd.to_numeric(
            pca_df[feature],
            errors="coerce"
        )

    pca_df = pca_df.dropna(subset=selected_features)

    if len(pca_df) < 3:
        return None, None, None

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        pca_df[selected_features]
    )

    pca = PCA(n_components=2)

    pca_values = pca.fit_transform(scaled_features)

    pca_df["PCA 1"] = pca_values[:, 0]
    pca_df["PCA 2"] = pca_values[:, 1]

    explained_variance = {
        "PCA 1 Explained Variance %": round(
            pca.explained_variance_ratio_[0] * 100,
            2
        ),
        "PCA 2 Explained Variance %": round(
            pca.explained_variance_ratio_[1] * 100,
            2
        ),
        "Total Explained Variance %": round(
            pca.explained_variance_ratio_.sum() * 100,
            2
        ),
    }

    component_loadings = pd.DataFrame(
        pca.components_.T,
        columns=["PCA 1", "PCA 2"],
        index=selected_features
    ).reset_index()

    component_loadings = component_loadings.rename(
        columns={"index": "Feature"}
    )

    component_loadings["PCA 1"] = component_loadings["PCA 1"].round(3)
    component_loadings["PCA 2"] = component_loadings["PCA 2"].round(3)

    return pca_df, explained_variance, component_loadings