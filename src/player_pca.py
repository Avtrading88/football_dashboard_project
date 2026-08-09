import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from src.feature_engineering import ordered_numeric_features, prepare_analytics_frame


def prepare_pca_data(df):
    """
    Prepare player data for PCA profile visualization.
    """

    pca_df = prepare_analytics_frame(df)

    if "Minutes Played" not in pca_df.columns:
        return pca_df

    pca_df = pca_df[
        pca_df["Minutes Played"].notna()
    ].copy()

    pca_df = pca_df[
        pca_df["Minutes Played"] > 0
    ].copy()

    return pca_df


def get_available_pca_features(df):
    """
    Return numeric columns available for PCA.
    """

    pca_df = prepare_pca_data(df)

    return ordered_numeric_features(pca_df)


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
