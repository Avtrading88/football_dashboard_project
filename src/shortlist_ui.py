"""Reusable Streamlit UI for transfer-shortlist workflows."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.player_radar import create_radar_comparison_data, get_available_radar_features
from src.scouting_exports import (
    build_scouting_report_pdf,
    prepare_shortlist_export_dataframe,
    shortlist_to_csv_bytes,
)
from src.shortlist_store import (
    RECRUITMENT_PRIORITIES,
    RECRUITMENT_STATUSES,
    add_or_refresh_shortlist_player,
    list_shortlist_entries,
    remove_shortlist_entry,
    update_shortlist_entry,
)


def _candidate_selection(candidates_df: pd.DataFrame) -> tuple[list[str], dict[str, str]]:
    required = {"Player Record ID", "Player Name"}
    if candidates_df.empty or not required.issubset(candidates_df.columns):
        return [], {}

    selection_columns = [
        column
        for column in [
            "Player Record ID",
            "Player Selection Label",
            "Player Name",
            "Club",
            "League",
        ]
        if column in candidates_df.columns
    ]
    selection_df = (
        candidates_df[selection_columns]
        .dropna(subset=["Player Record ID", "Player Name"])
        .drop_duplicates("Player Record ID")
        .copy()
    )
    if "Player Selection Label" not in selection_df.columns:
        club = selection_df.get("Club", pd.Series("Unknown club", index=selection_df.index))
        league = selection_df.get("League", pd.Series("Unknown league", index=selection_df.index))
        selection_df["Player Selection Label"] = (
            selection_df["Player Name"].astype(str)
            + " - "
            + club.astype(str)
            + " ("
            + league.astype(str)
            + ")"
        )

    selection_df = selection_df.sort_values("Player Selection Label")
    record_ids = selection_df["Player Record ID"].astype(str).tolist()
    labels = dict(
        zip(
            selection_df["Player Record ID"].astype(str),
            selection_df["Player Selection Label"].astype(str),
        )
    )
    return record_ids, labels


def render_shortlist_quick_add(
    candidates_df: pd.DataFrame,
    *,
    source_key: str,
    title: str = "Add a player to the transfer shortlist",
) -> None:
    """Render a compact, reusable shortlist action on analytics pages."""

    record_ids, labels = _candidate_selection(candidates_df)
    if not record_ids:
        return

    safe_key = source_key.lower().replace(" ", "_")
    with st.expander(f"⭐ {title}", expanded=False):
        action_col, button_col = st.columns([4, 1])
        with action_col:
            selected_id = st.selectbox(
                "Choose candidate",
                options=record_ids,
                format_func=lambda record_id: labels.get(record_id, record_id),
                key=f"shortlist_quick_add_select_{safe_key}",
            )
        with button_col:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            add_clicked = st.button(
                "Add to shortlist",
                key=f"shortlist_quick_add_button_{safe_key}",
                width="stretch",
            )

        if add_clicked:
            player_row = candidates_df[
                candidates_df["Player Record ID"].astype(str) == str(selected_id)
            ].iloc[0]
            entry = add_or_refresh_shortlist_player(
                player_row,
                source_page=source_key,
            )
            st.success(
                f"{entry['player_name']} was saved to the transfer shortlist."
            )


def _entry_label(entry: dict) -> str:
    return (
        f"{entry.get('player_name', 'Unknown player')} - "
        f"{entry.get('club') or 'Unknown club'} "
        f"[{entry.get('status', 'Watching')}]"
    )


def _workspace_dataframe(entries: list[dict]) -> pd.DataFrame:
    export_df = prepare_shortlist_export_dataframe(entries)
    preferred_columns = [
        "Player Name",
        "Club",
        "League",
        "Position",
        "Age",
        "Status",
        "Priority",
        "Scout Rating",
        "Target Fee EUR",
        "Goals per 90",
        "Assists per 90",
        "Defensive Actions per 90",
        "Notes",
    ]
    columns = [column for column in preferred_columns if column in export_df.columns]
    return export_df[columns] if columns else export_df


def _render_workspace(entries: list[dict]) -> None:
    st.markdown("### Recruitment Pipeline")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        selected_statuses = st.multiselect(
            "Filter by status",
            options=list(RECRUITMENT_STATUSES),
            default=list(RECRUITMENT_STATUSES),
            key="shortlist_status_filter",
        )
    with filter_col2:
        selected_priorities = st.multiselect(
            "Filter by priority",
            options=list(RECRUITMENT_PRIORITIES),
            default=list(RECRUITMENT_PRIORITIES),
            key="shortlist_priority_filter",
        )

    visible_entries = [
        entry
        for entry in entries
        if entry.get("status") in selected_statuses
        and entry.get("priority") in selected_priorities
    ]
    if visible_entries:
        st.dataframe(
            _workspace_dataframe(visible_entries),
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No shortlist candidates match the selected workflow filters.")

    st.markdown("---")
    st.markdown("### Edit Candidate")
    entry_by_id = {entry["player_record_id"]: entry for entry in entries}
    selected_id = st.selectbox(
        "Choose saved candidate",
        options=list(entry_by_id),
        format_func=lambda record_id: _entry_label(entry_by_id[record_id]),
        key="shortlist_edit_candidate",
    )
    selected_entry = entry_by_id[selected_id]
    form_key = selected_entry["player_record_id"]

    with st.form(f"shortlist_edit_form_{form_key}"):
        form_col1, form_col2 = st.columns(2)
        with form_col1:
            status = st.selectbox(
                "Recruitment status",
                options=list(RECRUITMENT_STATUSES),
                index=list(RECRUITMENT_STATUSES).index(selected_entry["status"]),
            )
            target_fee = st.number_input(
                "Target fee (EUR)",
                min_value=0.0,
                value=float(selected_entry.get("target_fee_eur") or 0.0),
                step=100000.0,
                help="Use 0 when no target fee has been estimated.",
            )
        with form_col2:
            priority = st.selectbox(
                "Priority",
                options=list(RECRUITMENT_PRIORITIES),
                index=list(RECRUITMENT_PRIORITIES).index(selected_entry["priority"]),
            )
            scout_rating = st.number_input(
                "Scout rating (0-100)",
                min_value=0.0,
                max_value=100.0,
                value=float(selected_entry.get("scout_rating") or 0.0),
                step=1.0,
            )

        notes = st.text_area(
            "Scout notes",
            value=selected_entry.get("notes") or "",
            height=140,
            placeholder="Add strengths, risks, tactical fit, follow-up actions, and live-scouting observations.",
        )
        save_clicked = st.form_submit_button(
            "Save recruitment update",
            type="primary",
            width="stretch",
        )

    if save_clicked:
        update_shortlist_entry(
            selected_id,
            status=status,
            priority=priority,
            target_fee_eur=target_fee or None,
            scout_rating=scout_rating or None,
            notes=notes,
        )
        st.success(f"Recruitment details updated for {selected_entry['player_name']}.")
        st.rerun()

    delete_col1, delete_col2 = st.columns([3, 1])
    with delete_col1:
        confirm_delete = st.checkbox(
            f"Confirm removal of {selected_entry['player_name']}",
            key=f"shortlist_confirm_delete_{selected_id}",
        )
    with delete_col2:
        delete_clicked = st.button(
            "Remove candidate",
            disabled=not confirm_delete,
            key=f"shortlist_delete_{selected_id}",
            width="stretch",
        )
    if delete_clicked:
        remove_shortlist_entry(selected_id)
        st.success(f"{selected_entry['player_name']} was removed from the shortlist.")
        st.rerun()


def _render_comparison(entries: list[dict], players_df: pd.DataFrame, theme: str) -> None:
    st.markdown("### Shortlist Comparison")
    st.caption(
        "Compare recruitment context and normalized football performance for two to five saved candidates."
    )
    entry_by_id = {entry["player_record_id"]: entry for entry in entries}
    all_ids = list(entry_by_id)
    selected_ids = st.multiselect(
        "Choose shortlisted players",
        options=all_ids,
        default=all_ids[: min(2, len(all_ids))],
        format_func=lambda record_id: _entry_label(entry_by_id[record_id]),
        max_selections=5,
        key="shortlist_compare_players",
    )
    if len(selected_ids) < 2:
        st.info("Choose at least two shortlist candidates for comparison.")
        return

    comparison_entries = [entry_by_id[record_id] for record_id in selected_ids]
    workflow_df = prepare_shortlist_export_dataframe(comparison_entries)
    workflow_columns = [
        column
        for column in [
            "Player Name",
            "Club",
            "Position",
            "Status",
            "Priority",
            "Scout Rating",
            "Target Fee EUR",
            "Notes",
        ]
        if column in workflow_df.columns
    ]
    st.dataframe(workflow_df[workflow_columns], width="stretch", hide_index=True)

    available_features = get_available_radar_features(players_df)
    default_features = [
        feature
        for feature in [
            "Goals per 90",
            "Assists per 90",
            "Shots on Target per 90",
            "Crosses per 90",
            "Defensive Actions per 90",
        ]
        if feature in available_features
    ]
    selected_features = st.multiselect(
        "Radar statistics",
        options=available_features,
        default=default_features,
        key="shortlist_compare_metrics",
    )
    min_minutes = st.slider(
        "Minimum minutes for comparison scaling",
        min_value=0,
        max_value=4000,
        value=500,
        step=100,
        key="shortlist_compare_min_minutes",
    )
    if len(selected_features) < 3:
        st.info("Choose at least three statistics to create the shortlist radar chart.")
        return

    radar_df, original_df = create_radar_comparison_data(
        players_df,
        selected_players=selected_ids,
        selected_features=selected_features,
        min_minutes=min_minutes,
    )
    if radar_df is None:
        st.warning(
            "Radar data is unavailable for these candidates. Try lowering the minutes filter or changing the statistics."
        )
        return

    text_color = "#102033" if theme == "light" else "#EAF2FF"
    grid_color = "rgba(65,90,120,0.25)" if theme == "light" else "rgba(212,226,245,0.25)"
    figure = go.Figure()
    categories = selected_features + [selected_features[0]]
    for _, row in radar_df.iterrows():
        values = [row[feature] for feature in selected_features]
        values.append(values[0])
        figure.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name=row.get("Player Selection Label", row.get("Player Name")),
                hovertemplate="<b>%{theta}</b><br>Score: %{r:.1f}/100<extra></extra>",
            )
        )
    figure.update_layout(
        polar={
            "radialaxis": {
                "visible": True,
                "range": [0, 100],
                "tickfont": {"color": text_color},
                "gridcolor": grid_color,
            },
            "angularaxis": {"tickfont": {"color": text_color}, "gridcolor": grid_color},
            "bgcolor": "rgba(0,0,0,0)",
        },
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": text_color},
        height=650,
        legend={"orientation": "h", "y": -0.16, "x": 0.5, "xanchor": "center"},
        margin={"l": 40, "r": 40, "t": 30, "b": 100},
    )
    st.plotly_chart(figure, width="stretch")

    original_columns = [
        column
        for column in [
            "Player Name",
            "Club",
            "League",
            "Position",
            "Age",
            "Minutes Played",
        ]
        + selected_features
        if column in original_df.columns
    ]
    st.dataframe(original_df[original_columns], width="stretch", hide_index=True)


def _render_exports(entries: list[dict]) -> None:
    st.markdown("### Export Recruitment Work")
    st.caption(
        "Download an operational CSV or a presentation-ready PDF scouting report."
    )
    entry_by_id = {entry["player_record_id"]: entry for entry in entries}
    selected_ids = st.multiselect(
        "Players included in the export",
        options=list(entry_by_id),
        default=list(entry_by_id),
        format_func=lambda record_id: _entry_label(entry_by_id[record_id]),
        key="shortlist_export_players",
    )
    if not selected_ids:
        st.info("Choose at least one candidate to enable exports.")
        return

    selected_entries = [entry_by_id[record_id] for record_id in selected_ids]
    date_stamp = datetime.now().strftime("%Y%m%d")
    csv_bytes = shortlist_to_csv_bytes(selected_entries)

    csv_col, pdf_col = st.columns(2)
    with csv_col:
        st.download_button(
            "Download shortlist CSV",
            data=csv_bytes,
            file_name=f"transfer_shortlist_{date_stamp}.csv",
            mime="text/csv",
            width="stretch",
        )

    with pdf_col:
        if len(selected_entries) > 20:
            st.warning("Select no more than 20 candidates for one PDF report.")
        else:
            pdf_bytes = build_scouting_report_pdf(selected_entries)
            st.download_button(
                "Download scouting PDF",
                data=pdf_bytes,
                file_name=f"scouting_report_{date_stamp}.pdf",
                mime="application/pdf",
                width="stretch",
            )

    st.info(
        "The shortlist database and reports are local to this project. The SQLite database is excluded from Git."
    )


def show_transfer_shortlist_page(players_df: pd.DataFrame, *, theme: str = "dark") -> None:
    """Show the complete persistent recruitment workspace."""

    st.subheader("Transfer Shortlist & Recruitment Workspace")
    st.markdown(
        "Save candidates, manage recruitment decisions, compare profiles, and export professional scouting reports."
    )
    render_shortlist_quick_add(
        players_df,
        source_key="Transfer Shortlist",
        title="Add a candidate from the complete player dataset",
    )

    entries = list_shortlist_entries()
    if not entries:
        st.info(
            "Your shortlist is empty. Add a candidate above or use the shortlist action on Players, Similarity, or Scouting."
        )
        return

    status_counts = pd.Series([entry["status"] for entry in entries]).value_counts()
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Saved candidates", len(entries))
    kpi2.metric("Priority candidates", int(status_counts.get("Priority", 0)))
    kpi3.metric("Contacted", int(status_counts.get("Contacted", 0)))
    rated = [entry["scout_rating"] for entry in entries if entry.get("scout_rating") is not None]
    kpi4.metric("Average scout rating", f"{sum(rated) / len(rated):.1f}" if rated else "-")

    workspace_tab, compare_tab, export_tab = st.tabs(
        ["Recruitment Pipeline", "Compare Candidates", "CSV & PDF Exports"]
    )
    with workspace_tab:
        _render_workspace(entries)
    with compare_tab:
        _render_comparison(entries, players_df, theme)
    with export_tab:
        _render_exports(entries)

