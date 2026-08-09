import re
import pandas as pd
import streamlit as st

from src.config import DATA_PATH
from src.feature_engineering import (
    BASE_NUMERIC_COLUMNS,
    add_derived_metrics,
    add_player_identity_columns,
)


def clean_league_name(value):
    """Remove short country codes from league names."""
    if pd.isna(value):
        return value

    value = str(value)
    value = re.sub(r"^[a-z]{2,3}\s+", "", value)

    return value.strip()


def convert_whole_number_columns_to_int(df):
    """
    Convert numeric columns to integers if all non-null values
    are whole numbers.
    """
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            non_null = df[col].dropna()

            if len(non_null) == 0:
                continue

            # If every value is a whole number, convert to Int64.
            if (non_null % 1 == 0).all():
                df[col] = df[col].astype("Int64")

    return df


@st.cache_data
def load_data():
    """Load the CSV and clean columns."""
    df = pd.read_csv(DATA_PATH)

    rename_columns = {
        "Rk": "Rank",
        "Player": "Player Name",
        "Nation": "Nationality",
        "Pos": "Position",
        "Squad": "Club",
        "Comp": "League",
        "Age": "Age",
        "Born": "Birth Year",
        "MP": "Matches Played",
        "Starts": "Starts",
        "Min": "Minutes Played",
        "90s": "Full Match Equivalents",
        "Gls": "Goals",
        "Ast": "Assists",
        "G+A": "Goals + Assists",
        "G-PK": "Non-Penalty Goals",
        "PK": "Penalty Goals",
        "PKatt": "Penalties Attempted",
        "CrdY": "Yellow Cards",
        "CrdR": "Red Cards",
        "G+A-PK": "Non-Penalty Goals + Assists",
        "Sh": "Shots",
        "SoT": "Shots on Target",
        "SoT%": "Shots on Target Percentage",
        "Sh/90": "Shots per 90",
        "SoT/90": "Shots on Target per 90",
        "G/Sh": "Goals per Shot",
        "G/SoT": "Goals per Shot on Target",
        "PK_stats_shooting": "Shooting Penalty Goals",
        "PKatt_stats_shooting": "Shooting Penalties Attempted",
        "Crs": "Crosses",
        "TklW": "Tackles Won",
        "Int": "Interceptions",
        "Fld": "Fouled",
        "CrdY_stats_misc": "Misc Yellow Cards",
        "CrdR_stats_misc": "Misc Red Cards",
        "2CrdY": "Second Yellow Cards",
        "Fls": "Fouls Committed",
        "OG": "Own Goals",
        "xG": "Expected Goals",
        "npxG": "Non-Penalty Expected Goals",
        "xAG": "Expected Assisted Goals",
        "npxG+xAG": "Non-Penalty xG + Expected Assists",
        "PrgC": "Progressive Carries",
        "PrgP": "Progressive Passes",
        "PrgR": "Progressive Passes Received",
        "W": "Wins",
        "D": "Draws",
        "L": "Losses",
        "CS": "Clean Sheets",
        "CS%": "Clean Sheet Percentage",
        "PKatt_stats_keeper": "Penalties Faced",
        "PKA": "Penalties Allowed",
        "PKsv": "Penalties Saved",
        "PKm": "Penalties Missed",
        "Mean Age": "Average Age",
        "Saves": "Saves",
        "SoTA": "Shots on Target Against",
        "Save%": "Save Percentage",
        "GA": "Goals Against",
        "GA90": "Goals Against per 90",
    }

    df = df.rename(columns=rename_columns)

    if "Nationality" in df.columns:
        df["Nationality"] = df["Nationality"].astype("string").str.replace(
            r"^[a-z]{2,3}\s+",
            "",
            regex=True
        )

    if "League" in df.columns:
        df["League"] = df["League"].apply(clean_league_name)

    numeric_columns = BASE_NUMERIC_COLUMNS + [
        "Non-Penalty Goals + Assists",
        "Shooting Penalty Goals",
        "Shooting Penalties Attempted",
        "Misc Yellow Cards",
        "Misc Red Cards",
        "Average Age",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = add_player_identity_columns(df)
    df = add_derived_metrics(df)

    # Convert whole-number numeric columns into integers.
    df = convert_whole_number_columns_to_int(df)

    return df
