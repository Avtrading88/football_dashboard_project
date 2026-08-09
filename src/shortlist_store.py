"""Persistent transfer-shortlist storage backed by SQLite."""

from __future__ import annotations

import json
import math
import sqlite3
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SHORTLIST_DB_PATH = PROJECT_ROOT / "data" / "transfer_shortlist.sqlite3"

RECRUITMENT_STATUSES = (
    "Watching",
    "Scouted",
    "Priority",
    "Contacted",
    "Rejected",
)

RECRUITMENT_PRIORITIES = (
    "Low",
    "Medium",
    "High",
    "Critical",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(db_path or DEFAULT_SHORTLIST_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


@contextmanager
def _managed_connection(
    db_path: str | Path | None = None,
) -> Iterator[sqlite3.Connection]:
    """Commit or roll back a transaction and always release the database file."""

    connection = _connect(db_path)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_shortlist_database(db_path: str | Path | None = None) -> Path:
    """Create the shortlist database and return its resolved path."""

    path = Path(db_path or DEFAULT_SHORTLIST_DB_PATH)
    with _managed_connection(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS shortlist_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_record_id TEXT NOT NULL UNIQUE,
                player_id TEXT,
                player_name TEXT NOT NULL,
                nationality TEXT,
                position TEXT,
                club TEXT,
                league TEXT,
                age REAL,
                source_page TEXT NOT NULL DEFAULT 'Transfer Shortlist',
                status TEXT NOT NULL DEFAULT 'Watching',
                priority TEXT NOT NULL DEFAULT 'Medium',
                target_fee_eur REAL,
                scout_rating REAL,
                notes TEXT NOT NULL DEFAULT '',
                snapshot_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
    return path.resolve()


def _json_safe(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except (TypeError, ValueError):
            pass
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _player_mapping(player: Mapping[str, Any] | pd.Series) -> dict[str, Any]:
    if isinstance(player, pd.Series):
        player = player.to_dict()
    return {str(key): _json_safe(value) for key, value in dict(player).items()}


def add_or_refresh_shortlist_player(
    player: Mapping[str, Any] | pd.Series,
    source_page: str = "Transfer Shortlist",
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    """Add a player or refresh its statistics without overwriting scout work."""

    initialize_shortlist_database(db_path)
    snapshot = _player_mapping(player)
    player_record_id = str(snapshot.get("Player Record ID") or "").strip()
    player_name = str(snapshot.get("Player Name") or "").strip()
    if not player_record_id:
        raise ValueError("Player Record ID is required to save a shortlist entry.")
    if not player_name:
        raise ValueError("Player Name is required to save a shortlist entry.")

    now = _utc_now()
    values = {
        "player_record_id": player_record_id,
        "player_id": snapshot.get("Player ID"),
        "player_name": player_name,
        "nationality": snapshot.get("Nationality"),
        "position": snapshot.get("Position"),
        "club": snapshot.get("Club"),
        "league": snapshot.get("League"),
        "age": snapshot.get("Age"),
        "source_page": str(source_page or "Transfer Shortlist"),
        "snapshot_json": json.dumps(snapshot, ensure_ascii=False, sort_keys=True),
        "created_at": now,
        "updated_at": now,
    }

    with _managed_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO shortlist_entries (
                player_record_id, player_id, player_name, nationality,
                position, club, league, age, source_page, snapshot_json,
                created_at, updated_at
            ) VALUES (
                :player_record_id, :player_id, :player_name, :nationality,
                :position, :club, :league, :age, :source_page, :snapshot_json,
                :created_at, :updated_at
            )
            ON CONFLICT(player_record_id) DO UPDATE SET
                player_id = excluded.player_id,
                player_name = excluded.player_name,
                nationality = excluded.nationality,
                position = excluded.position,
                club = excluded.club,
                league = excluded.league,
                age = excluded.age,
                source_page = excluded.source_page,
                snapshot_json = excluded.snapshot_json,
                updated_at = excluded.updated_at
            """,
            values,
        )

    return get_shortlist_entry(player_record_id, db_path=db_path)


def _validate_status(status: str) -> str:
    if status not in RECRUITMENT_STATUSES:
        raise ValueError(f"Unsupported recruitment status: {status}")
    return status


def _validate_priority(priority: str) -> str:
    if priority not in RECRUITMENT_PRIORITIES:
        raise ValueError(f"Unsupported recruitment priority: {priority}")
    return priority


def _optional_non_negative_number(value: Any, label: str) -> float | None:
    if value in (None, ""):
        return None
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{label} must be a non-negative number.")
    return result


def update_shortlist_entry(
    player_record_id: str,
    *,
    status: str,
    priority: str,
    target_fee_eur: float | None = None,
    scout_rating: float | None = None,
    notes: str = "",
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    """Update recruitment workflow fields for one saved candidate."""

    initialize_shortlist_database(db_path)
    status = _validate_status(status)
    priority = _validate_priority(priority)
    target_fee_eur = _optional_non_negative_number(target_fee_eur, "Target fee")
    scout_rating = _optional_non_negative_number(scout_rating, "Scout rating")
    if scout_rating is not None and scout_rating > 100:
        raise ValueError("Scout rating must be between 0 and 100.")

    with _managed_connection(db_path) as connection:
        cursor = connection.execute(
            """
            UPDATE shortlist_entries
            SET status = ?, priority = ?, target_fee_eur = ?,
                scout_rating = ?, notes = ?, updated_at = ?
            WHERE player_record_id = ?
            """,
            (
                status,
                priority,
                target_fee_eur,
                scout_rating,
                str(notes or "").strip(),
                _utc_now(),
                str(player_record_id),
            ),
        )
        if cursor.rowcount != 1:
            raise KeyError(f"Shortlist player not found: {player_record_id}")

    return get_shortlist_entry(player_record_id, db_path=db_path)


def get_shortlist_entry(
    player_record_id: str,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    initialize_shortlist_database(db_path)
    with _managed_connection(db_path) as connection:
        row = connection.execute(
            "SELECT * FROM shortlist_entries WHERE player_record_id = ?",
            (str(player_record_id),),
        ).fetchone()
    if row is None:
        raise KeyError(f"Shortlist player not found: {player_record_id}")
    return dict(row)


def list_shortlist_entries(
    *,
    statuses: list[str] | tuple[str, ...] | None = None,
    priorities: list[str] | tuple[str, ...] | None = None,
    db_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Return candidates ordered by recruitment priority and update time."""

    initialize_shortlist_database(db_path)
    clauses: list[str] = []
    parameters: list[Any] = []

    if statuses:
        statuses = [_validate_status(status) for status in statuses]
        clauses.append("status IN ({})".format(",".join("?" for _ in statuses)))
        parameters.extend(statuses)
    if priorities:
        priorities = [_validate_priority(priority) for priority in priorities]
        clauses.append("priority IN ({})".format(",".join("?" for _ in priorities)))
        parameters.extend(priorities)

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"""
        SELECT * FROM shortlist_entries
        {where_sql}
        ORDER BY
            CASE priority
                WHEN 'Critical' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                ELSE 4
            END,
            updated_at DESC,
            player_name ASC
    """

    with _managed_connection(db_path) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [dict(row) for row in rows]


def remove_shortlist_entry(
    player_record_id: str,
    db_path: str | Path | None = None,
) -> bool:
    initialize_shortlist_database(db_path)
    with _managed_connection(db_path) as connection:
        cursor = connection.execute(
            "DELETE FROM shortlist_entries WHERE player_record_id = ?",
            (str(player_record_id),),
        )
    return cursor.rowcount == 1


def decode_snapshot(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Decode the saved player-statistics snapshot for display and export."""

    value = entry.get("snapshot_json", "{}")
    if isinstance(value, Mapping):
        return dict(value)
    try:
        decoded = json.loads(value or "{}")
    except (TypeError, json.JSONDecodeError):
        return {}
    return decoded if isinstance(decoded, dict) else {}
