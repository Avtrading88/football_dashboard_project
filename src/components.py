import pandas as pd
import streamlit as st


def kpi_card(label, value, change_text=""):
    """Show one KPI card."""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-change">{change_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def centered_dataframe(df):
    """Show a table with centered text and clean number formatting."""

    display_df = df.copy()

    # Format numeric columns nicely.
    for col in display_df.columns:
        if pd.api.types.is_numeric_dtype(display_df[col]):
            non_null = display_df[col].dropna()

            if len(non_null) == 0:
                continue

            # Show whole numbers as integers.
            if (non_null % 1 == 0).all():
                display_df[col] = display_df[col].apply(
                    lambda x: f"{int(x)}" if pd.notna(x) else ""
                )
            else:
                # Keep real decimals, but make them nicer.
                display_df[col] = display_df[col].apply(
                    lambda x: f"{x:.2f}" if pd.notna(x) else ""
                )

    styled_df = (
        display_df.style
        .set_properties(**{
            "text-align": "center",
            "color": "#F8FAFC",
            "background-color": "#071426",
        })
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("text-align", "center"),
                    ("color", "#B7FF3C"),
                    ("background-color", "#0B1728"),
                    ("font-weight", "800"),
                ],
            },
            {
                "selector": "td",
                "props": [
                    ("text-align", "center"),
                ],
            },
        ])
    )

    st.dataframe(
        styled_df,
        width="stretch",
        hide_index=True
    )