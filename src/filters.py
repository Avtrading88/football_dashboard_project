import streamlit as st


def apply_sidebar_filters(players_df):
    """Build sidebar filters and return filtered data."""
    st.sidebar.markdown(
        """
        <div class="sidebar-hero">
            <div class="sidebar-hero-icon">⚽</div>
            <div>
                <div class="sidebar-hero-title">Football Dashboard</div>
                <div class="sidebar-hero-subtitle">
                    Customize your player analytics view.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    filtered_df = players_df.copy()
    min_age = int(players_df["Age"].min()) if "Age" in players_df.columns else 15
    max_age = int(players_df["Age"].max()) if "Age" in players_df.columns else 40

    with st.sidebar.expander("🏆 League Filter", expanded=True):
        league_options = sorted(players_df["League"].dropna().unique())
        selected_leagues = st.multiselect(
            "Choose league(s)",
            options=league_options,
            placeholder="All leagues"
        )
    if selected_leagues:
        filtered_df = filtered_df[filtered_df["League"].isin(selected_leagues)]

    with st.sidebar.expander("🛡️ Club Filter", expanded=True):
        club_options = sorted(filtered_df["Club"].dropna().unique())
        selected_clubs = st.multiselect(
            "Choose club(s)",
            options=club_options,
            placeholder="All clubs"
        )
    if selected_clubs:
        filtered_df = filtered_df[filtered_df["Club"].isin(selected_clubs)]

    with st.sidebar.expander("📍 Position Filter", expanded=True):
        position_column = (
            "Primary Position"
            if "Primary Position" in filtered_df.columns
            else "Position"
        )
        position_options = sorted(filtered_df[position_column].dropna().unique())
        selected_positions = st.multiselect(
            "Choose primary position(s)",
            options=position_options,
            placeholder="All positions"
        )
    if selected_positions:
        filtered_df = filtered_df[
            filtered_df[position_column].isin(selected_positions)
        ]

    with st.sidebar.expander("🌍 Nationality Filter", expanded=False):
        nationality_options = sorted(filtered_df["Nationality"].dropna().unique())
        selected_nationalities = st.multiselect(
            "Choose nationality(s)",
            options=nationality_options,
            placeholder="All nationalities"
        )
    if selected_nationalities:
        filtered_df = filtered_df[filtered_df["Nationality"].isin(selected_nationalities)]

    with st.sidebar.expander("🎂 Age Filter", expanded=False):
        if "Age" in filtered_df.columns:
            selected_age_range = st.slider(
                "Age range",
                min_value=min_age,
                max_value=max_age,
                value=(min_age, max_age)
            )
            filtered_df = filtered_df[
                filtered_df["Age"].between(selected_age_range[0], selected_age_range[1])
            ]

    with st.sidebar.expander("📊 Performance Filter", expanded=True):
        if "Minutes Played" in filtered_df.columns:
            max_minutes = int(players_df["Minutes Played"].max())
            min_minutes = st.slider(
                "Minimum minutes played",
                0,
                max_minutes,
                0,
                step=100,
            )
            filtered_df = filtered_df[
                filtered_df["Minutes Played"] >= min_minutes
            ]

        if "Matches Played" in filtered_df.columns:
            max_matches = int(players_df["Matches Played"].max())
            min_matches = st.slider("Minimum matches played", 0, max_matches, 0)
            filtered_df = filtered_df[filtered_df["Matches Played"] >= min_matches]

        if "Goals" in filtered_df.columns:
            max_goals = int(players_df["Goals"].max())
            min_goals = st.slider("Minimum goals", 0, max_goals, 0)
            filtered_df = filtered_df[filtered_df["Goals"] >= min_goals]

        if "Assists" in filtered_df.columns:
            max_assists = int(players_df["Assists"].max())
            min_assists = st.slider("Minimum assists", 0, max_assists, 0)
            filtered_df = filtered_df[filtered_df["Assists"] >= min_assists]

    with st.sidebar.expander("🔎 Player Search", expanded=False):
        player_search = st.text_input("Search player")
    if player_search:
        filtered_df = filtered_df[
            filtered_df["Player Name"].astype(str).str.contains(player_search, case=False, na=False)
        ]

    return filtered_df
