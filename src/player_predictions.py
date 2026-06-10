import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


def prepare_prediction_data(df):
    """
    Prepare data for prediction models and advanced football metrics.
    """

    model_df = df.copy()

    useful_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
        "Age",
        "Minutes Played",
        "Matches Played",
        "Starts",
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
        if col in model_df.columns
    ]

    model_df = model_df[existing_columns].copy()

    text_columns = [
        "Player Name",
        "Nationality",
        "Position",
        "Club",
        "League",
    ]

    numeric_columns = [
        col for col in model_df.columns
        if col not in text_columns
    ]

    for col in numeric_columns:
        model_df[col] = pd.to_numeric(
            model_df[col],
            errors="coerce"
        )

    if "Minutes Played" in model_df.columns:
        model_df = model_df[
            model_df["Minutes Played"].fillna(0) > 0
        ].copy()

    if "Goals" in model_df.columns and "Minutes Played" in model_df.columns:
        model_df["Goals per 90"] = (
            model_df["Goals"] / model_df["Minutes Played"] * 90
        )

    if "Assists" in model_df.columns and "Minutes Played" in model_df.columns:
        model_df["Assists per 90"] = (
            model_df["Assists"] / model_df["Minutes Played"] * 90
        )

    if (
        "Goals" in model_df.columns
        and "Assists" in model_df.columns
        and "Minutes Played" in model_df.columns
    ):
        model_df["Goals + Assists per 90"] = (
            (model_df["Goals"] + model_df["Assists"])
            / model_df["Minutes Played"]
            * 90
        )

    if "Expected Goals" in model_df.columns and "Goals" in model_df.columns:
        model_df["Goals minus xG"] = (
            model_df["Goals"] - model_df["Expected Goals"]
        )

        model_df["Goal Efficiency Ratio"] = (
            model_df["Goals"] / model_df["Expected Goals"].replace(0, pd.NA)
        )

    if (
        "Expected Assisted Goals" in model_df.columns
        and "Assists" in model_df.columns
    ):
        model_df["Assists minus xAG"] = (
            model_df["Assists"] - model_df["Expected Assisted Goals"]
        )

    if "Expected Goals" in model_df.columns and "Minutes Played" in model_df.columns:
        model_df["Expected Goals per 90"] = (
            model_df["Expected Goals"] / model_df["Minutes Played"] * 90
        )

    if "Expected Assisted Goals" in model_df.columns and "Minutes Played" in model_df.columns:
        model_df["Expected Assisted Goals per 90"] = (
            model_df["Expected Assisted Goals"]
            / model_df["Minutes Played"]
            * 90
        )

    if (
        "Expected Goals" in model_df.columns
        and "Expected Assisted Goals" in model_df.columns
        and "Minutes Played" in model_df.columns
    ):
        model_df["Expected Goals + Expected Assists per 90"] = (
            (
                model_df["Expected Goals"]
                + model_df["Expected Assisted Goals"]
            )
            / model_df["Minutes Played"]
            * 90
        )

    if "Progressive Carries" in model_df.columns and "Minutes Played" in model_df.columns:
        model_df["Progressive Carries per 90"] = (
            model_df["Progressive Carries"]
            / model_df["Minutes Played"]
            * 90
        )

    if "Progressive Passes" in model_df.columns and "Minutes Played" in model_df.columns:
        model_df["Progressive Passes per 90"] = (
            model_df["Progressive Passes"]
            / model_df["Minutes Played"]
            * 90
        )

    if (
        "Progressive Carries" in model_df.columns
        and "Progressive Passes" in model_df.columns
    ):
        model_df["Total Progressive Actions"] = (
            model_df["Progressive Carries"]
            + model_df["Progressive Passes"]
        )

    if "Yellow Cards" in model_df.columns and "Red Cards" in model_df.columns:
        model_df["Discipline Risk"] = (
            model_df["Yellow Cards"] + model_df["Red Cards"] * 3
        )

    return model_df


def get_model_feature_columns(model_df, target_type="goals"):
    """
    Select safe model features.
    Avoid direct target leakage where possible.
    """

    base_numeric_features = [
        "Age",
        "Minutes Played",
        "Matches Played",
        "Starts",
        "Assists",
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

    # For classification, avoid using direct Goals/Assists output as predictors
    # because the class target is based on Goals + Assists per 90.
    if target_type == "top_performer":
        base_numeric_features = [
            "Age",
            "Minutes Played",
            "Matches Played",
            "Starts",
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

    categorical_features = [
        "Position",
        "League",
    ]

    numeric_features = [
        col for col in base_numeric_features
        if col in model_df.columns
    ]

    categorical_features = [
        col for col in categorical_features
        if col in model_df.columns
    ]

    return numeric_features, categorical_features


def build_preprocessor(numeric_features, categorical_features):
    """
    Build preprocessing pipeline for numeric and categorical features.
    """

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features
            )
        ],
        remainder="passthrough"
    )

    return preprocessor


def train_goals_prediction_model(df, min_minutes=500):
    """
    Option A:
    Train a RandomForestRegressor to predict player goals.
    """

    model_df = prepare_prediction_data(df)

    if "Minutes Played" in model_df.columns:
        model_df = model_df[
            model_df["Minutes Played"] >= min_minutes
        ].copy()

    if "Goals" not in model_df.columns:
        return None, None, None

    numeric_features, categorical_features = get_model_feature_columns(
        model_df,
        target_type="goals"
    )

    feature_columns = categorical_features + numeric_features

    model_df = model_df.dropna(
        subset=feature_columns + ["Goals"]
    ).copy()

    if len(model_df) < 30:
        return None, None, None

    X = model_df[feature_columns]
    y = model_df["Goals"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42
    )

    preprocessor = build_preprocessor(
        numeric_features=numeric_features,
        categorical_features=categorical_features
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=300,
                    random_state=42,
                    n_jobs=-1,
                    max_depth=8
                )
            )
        ]
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    metrics = {
        "MAE": round(mean_absolute_error(y_test, predictions), 2),
        "RMSE": round(mean_squared_error(y_test, predictions) ** 0.5, 2),
        "R2 Score": round(r2_score(y_test, predictions), 3),
        "Training Rows": len(X_train),
        "Test Rows": len(X_test),
    }

    model_df["Predicted Goals"] = model.predict(model_df[feature_columns])
    model_df["Predicted Goals"] = model_df["Predicted Goals"].round(1)

    model_df["Goal Difference vs Prediction"] = (
        model_df["Goals"] - model_df["Predicted Goals"]
    ).round(1)

    model_df = model_df.sort_values(
        "Predicted Goals",
        ascending=False
    )

    return model_df, metrics, feature_columns


def train_top_performer_classifier(
    df,
    min_minutes=500,
    top_percentile=75
):
    """
    Option B:
    Train a RandomForestClassifier to predict whether a player is a top performer.
    Target is based on Goals + Assists per 90.
    """

    model_df = prepare_prediction_data(df)

    if "Minutes Played" in model_df.columns:
        model_df = model_df[
            model_df["Minutes Played"] >= min_minutes
        ].copy()

    if "Goals + Assists per 90" not in model_df.columns:
        return None, None, None

    threshold = model_df["Goals + Assists per 90"].quantile(
        top_percentile / 100
    )

    model_df["Top Performer"] = (
        model_df["Goals + Assists per 90"] >= threshold
    ).astype(int)

    numeric_features, categorical_features = get_model_feature_columns(
        model_df,
        target_type="top_performer"
    )

    feature_columns = categorical_features + numeric_features

    model_df = model_df.dropna(
        subset=feature_columns + ["Top Performer"]
    ).copy()

    if len(model_df) < 30 or model_df["Top Performer"].nunique() < 2:
        return None, None, None

    X = model_df[feature_columns]
    y = model_df["Top Performer"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    preprocessor = build_preprocessor(
        numeric_features=numeric_features,
        categorical_features=categorical_features
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=300,
                    random_state=42,
                    n_jobs=-1,
                    max_depth=8,
                    class_weight="balanced"
                )
            )
        ]
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = {
        "Accuracy": round(accuracy_score(y_test, predictions), 3),
        "F1 Score": round(f1_score(y_test, predictions), 3),
        "Top Performer Threshold": round(threshold, 3),
        "Training Rows": len(X_train),
        "Test Rows": len(X_test),
    }

    model_df["Top Performer Probability"] = (
        model.predict_proba(model_df[feature_columns])[:, 1] * 100
    ).round(1)

    model_df["Predicted Top Performer"] = model.predict(
        model_df[feature_columns]
    )

    model_df["Predicted Label"] = model_df["Predicted Top Performer"].map(
        {
            1: "Top Performer",
            0: "Not Top Performer"
        }
    )

    model_df = model_df.sort_values(
        "Top Performer Probability",
        ascending=False
    )

    return model_df, metrics, feature_columns


def create_advanced_metrics_table(df, min_minutes=500):
    """
    Create advanced metrics table for xG and football performance analysis.
    """

    metrics_df = prepare_prediction_data(df)

    if "Minutes Played" in metrics_df.columns:
        metrics_df = metrics_df[
            metrics_df["Minutes Played"] >= min_minutes
        ].copy()

    if metrics_df.empty:
        return None

    metrics_df = metrics_df.sort_values(
        "Goals + Assists per 90"
        if "Goals + Assists per 90" in metrics_df.columns
        else "Minutes Played",
        ascending=False
    )

    return metrics_df