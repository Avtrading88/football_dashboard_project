"""Shared football feature engineering and player identity helpers."""

from __future__ import annotations

import hashlib
import re

import pandas as pd


PLAYER_CONTEXT_COLUMNS = [
    "Player ID",
    "Player Record ID",
    "Player Selection Label",
    "Player Name",
    "Nationality",
    "Position",
    "Primary Position",
    "Club",
    "League",
]


BASE_NUMERIC_COLUMNS = [
    "Age",
    "Birth Year",
    "Matches Played",
    "Starts",
    "Minutes Played",
    "Full Match Equivalents",
    "Goals",
    "Assists",
    "Goals + Assists",
    "Non-Penalty Goals",
    "Penalty Goals",
    "Penalties Attempted",
    "Yellow Cards",
    "Red Cards",
    "Shots",
    "Shots on Target",
    "Shots on Target Percentage",
    "Shots per 90",
    "Shots on Target per 90",
    "Goals per Shot",
    "Goals per Shot on Target",
    "Crosses",
    "Tackles Won",
    "Interceptions",
    "Fouled",
    "Second Yellow Cards",
    "Fouls Committed",
    "Own Goals",
    "Expected Goals",
    "Non-Penalty Expected Goals",
    "Expected Assisted Goals",
    "Non-Penalty xG + Expected Assists",
    "Progressive Carries",
    "Progressive Passes",
    "Progressive Passes Received",
    "Wins",
    "Draws",
    "Losses",
    "Clean Sheets",
    "Clean Sheet Percentage",
    "Shots on Target Against",
    "Saves",
    "Save Percentage",
    "Goals Against",
    "Goals Against per 90",
    "Penalties Faced",
    "Penalties Allowed",
    "Penalties Saved",
    "Penalties Missed",
]


DERIVED_NUMERIC_COLUMNS = [
    "Goals per 90",
    "Non-Penalty Goals per 90",
    "Assists per 90",
    "Goals + Assists per 90",
    "Expected Goals per 90",
    "Expected Assisted Goals per 90",
    "Expected Goals + Expected Assists per 90",
    "Progressive Carries per 90",
    "Progressive Passes per 90",
    "Progressive Passes Received per 90",
    "Crosses per 90",
    "Tackles Won per 90",
    "Interceptions per 90",
    "Defensive Actions",
    "Defensive Actions per 90",
    "Fouled per 90",
    "Fouls Committed per 90",
    "Yellow Cards per 90",
    "Red Cards per 90",
    "Goal Conversion Percentage",
    "Shot Accuracy Percentage",
    "Penalty Save Percentage",
    "Discipline Risk",
    "Discipline Risk per 90",
]


ANALYTICS_NUMERIC_COLUMNS = list(
    dict.fromkeys(BASE_NUMERIC_COLUMNS + DERIVED_NUMERIC_COLUMNS)
)


PREFERRED_ANALYTICS_ORDER = [
    "Age",
    "Minutes Played",
    "Matches Played",
    "Goals per 90",
    "Non-Penalty Goals per 90",
    "Assists per 90",
    "Goals + Assists per 90",
    "Shots per 90",
    "Shots on Target per 90",
    "Shot Accuracy Percentage",
    "Goal Conversion Percentage",
    "Crosses per 90",
    "Tackles Won per 90",
    "Interceptions per 90",
    "Defensive Actions per 90",
    "Fouled per 90",
    "Fouls Committed per 90",
    "Yellow Cards per 90",
    "Red Cards per 90",
    "Expected Goals per 90",
    "Expected Assisted Goals per 90",
    "Expected Goals + Expected Assists per 90",
    "Progressive Carries per 90",
    "Progressive Passes per 90",
    "Progressive Passes Received per 90",
    "Save Percentage",
    "Clean Sheet Percentage",
    "Goals Against per 90",
    "Penalty Save Percentage",
    "Goals",
    "Assists",
    "Shots",
    "Shots on Target",
    "Crosses",
    "Tackles Won",
    "Interceptions",
    "Yellow Cards",
    "Red Cards",
]


def _normalise_identity_part(value) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip().casefold())


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def add_player_identity_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add stable player and player-club record identifiers.

    The source snapshot has no provider ID. Name, birth year and nationality
    therefore form the best available player identity. A separate record ID
    preserves club rows for players who transferred during the season.
    """

    result = df.copy()

    def player_identity(row) -> str:
        source = "|".join(
            [
                _normalise_identity_part(row.get("Player Name")),
                _normalise_identity_part(row.get("Birth Year")),
                _normalise_identity_part(row.get("Nationality")),
            ]
        )
        return f"player_{_short_hash(source)}"

    result["Player ID"] = result.apply(player_identity, axis=1)

    result["Player Record ID"] = result.apply(
        lambda row: "record_"
        + _short_hash(
            "|".join(
                [
                    _normalise_identity_part(row.get("Player ID")),
                    _normalise_identity_part(row.get("Club")),
                    _normalise_identity_part(row.get("League")),
                ]
            )
        ),
        axis=1,
    )

    player_name = result.get("Player Name", pd.Series("Unknown", index=result.index))
    club = result.get("Club", pd.Series("Unknown club", index=result.index))
    league = result.get("League", pd.Series("Unknown league", index=result.index))

    result["Player Selection Label"] = (
        player_name.astype("string").fillna("Unknown player")
        + " — "
        + club.astype("string").fillna("Unknown club")
        + " ("
        + league.astype("string").fillna("Unknown league")
        + ")"
    )

    return result


def _safe_ratio(
    numerator: pd.Series,
    denominator: pd.Series,
    multiplier: float = 1.0,
) -> pd.Series:
    numerator = pd.to_numeric(numerator, errors="coerce")
    denominator = pd.to_numeric(denominator, errors="coerce")
    valid_denominator = denominator.where(denominator > 0)
    return numerator.div(valid_denominator).mul(multiplier)


def _add_per_90(
    df: pd.DataFrame,
    source_column: str,
    target_column: str,
) -> None:
    if source_column in df.columns and "Minutes Played" in df.columns:
        df[target_column] = _safe_ratio(
            df[source_column],
            df["Minutes Played"],
            multiplier=90,
        )


def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce football metrics and calculate reusable per-90/rate features."""

    result = df.copy()

    for column in BASE_NUMERIC_COLUMNS:
        if column in result.columns:
            result[column] = pd.to_numeric(result[column], errors="coerce")

    if "Position" in result.columns:
        result["Primary Position"] = (
            result["Position"]
            .astype("string")
            .str.split(",")
            .str[0]
            .str.strip()
        )

    per_90_columns = {
        "Goals": "Goals per 90",
        "Non-Penalty Goals": "Non-Penalty Goals per 90",
        "Assists": "Assists per 90",
        "Goals + Assists": "Goals + Assists per 90",
        "Expected Goals": "Expected Goals per 90",
        "Expected Assisted Goals": "Expected Assisted Goals per 90",
        "Progressive Carries": "Progressive Carries per 90",
        "Progressive Passes": "Progressive Passes per 90",
        "Progressive Passes Received": "Progressive Passes Received per 90",
        "Crosses": "Crosses per 90",
        "Tackles Won": "Tackles Won per 90",
        "Interceptions": "Interceptions per 90",
        "Fouled": "Fouled per 90",
        "Fouls Committed": "Fouls Committed per 90",
        "Yellow Cards": "Yellow Cards per 90",
        "Red Cards": "Red Cards per 90",
    }

    for source_column, target_column in per_90_columns.items():
        _add_per_90(result, source_column, target_column)

    if "Expected Goals" in result.columns and "Expected Assisted Goals" in result.columns:
        expected_output = result["Expected Goals"] + result["Expected Assisted Goals"]
        if "Minutes Played" in result.columns:
            result["Expected Goals + Expected Assists per 90"] = _safe_ratio(
                expected_output,
                result["Minutes Played"],
                multiplier=90,
            )

    if "Tackles Won" in result.columns and "Interceptions" in result.columns:
        result["Defensive Actions"] = result["Tackles Won"] + result["Interceptions"]
        _add_per_90(result, "Defensive Actions", "Defensive Actions per 90")

    if "Goals per Shot" in result.columns:
        result["Goal Conversion Percentage"] = result["Goals per Shot"] * 100
    elif "Non-Penalty Goals" in result.columns and "Shots" in result.columns:
        result["Goal Conversion Percentage"] = _safe_ratio(
            result["Non-Penalty Goals"],
            result["Shots"],
            multiplier=100,
        )

    if "Shots on Target Percentage" in result.columns:
        result["Shot Accuracy Percentage"] = result["Shots on Target Percentage"]
    elif "Shots on Target" in result.columns and "Shots" in result.columns:
        result["Shot Accuracy Percentage"] = _safe_ratio(
            result["Shots on Target"],
            result["Shots"],
            multiplier=100,
        )

    if "Penalties Saved" in result.columns and "Penalties Faced" in result.columns:
        result["Penalty Save Percentage"] = _safe_ratio(
            result["Penalties Saved"],
            result["Penalties Faced"],
            multiplier=100,
        )

    if "Yellow Cards" in result.columns and "Red Cards" in result.columns:
        result["Discipline Risk"] = result["Yellow Cards"] + result["Red Cards"] * 3
        _add_per_90(result, "Discipline Risk", "Discipline Risk per 90")

    return result


def prepare_analytics_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Return one consistent analytics frame used by all modelling modules."""

    result = add_derived_metrics(df)
    if "Player ID" not in result.columns or "Player Record ID" not in result.columns:
        result = add_player_identity_columns(result)

    selected_columns = PLAYER_CONTEXT_COLUMNS + ANALYTICS_NUMERIC_COLUMNS
    selected_columns = [column for column in selected_columns if column in result.columns]
    return result[selected_columns].copy()


def ordered_numeric_features(df: pd.DataFrame) -> list[str]:
    """Return numeric football features in a useful dashboard order."""

    numeric_columns = [
        column
        for column in df.columns
        if column not in PLAYER_CONTEXT_COLUMNS
        and pd.api.types.is_numeric_dtype(df[column])
    ]
    preferred = [
        column for column in PREFERRED_ANALYTICS_ORDER if column in numeric_columns
    ]
    remaining = [column for column in numeric_columns if column not in preferred]
    return preferred + remaining
