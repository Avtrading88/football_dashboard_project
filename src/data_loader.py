import re
import pandas as pd
import streamlit as st

from src.config import DATA_PATH


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
        "GA": "Goals Against",
        "GA90": "Goals Against per 90",
    }

    df = df.rename(columns=rename_columns)

    if "Nationality" in df.columns:
        df["Nationality"] = df["Nationality"].astype(str).str.replace(
            r"^[a-z]{2,3}\s+",
            "",
            regex=True
        )

    if "League" in df.columns:
        df["League"] = df["League"].apply(clean_league_name)

    numeric_columns = [
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
        "Penalties Faced",
        "Penalties Allowed",
        "Penalties Saved",
        "Penalties Missed",
        "Average Age",
        "Saves",
        "Goals Against",
        "Goals Against per 90",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Convert whole-number numeric columns into integers.
    df = convert_whole_number_columns_to_int(df)

    return df