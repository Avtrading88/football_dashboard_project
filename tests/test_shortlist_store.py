import json
import tempfile
import unittest
from pathlib import Path

from src.shortlist_store import (
    add_or_refresh_shortlist_player,
    get_shortlist_entry,
    list_shortlist_entries,
    remove_shortlist_entry,
    update_shortlist_entry,
)


class ShortlistStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_directory.name) / "shortlist.sqlite3"
        self.player = {
            "Player ID": "player_1",
            "Player Record ID": "record_1",
            "Player Name": "Test Forward",
            "Nationality": "Germany",
            "Position": "FW",
            "Club": "Analytics FC",
            "League": "Bundesliga",
            "Age": 21,
            "Goals": 10,
            "Assists": 5,
            "Goals per 90": 0.5,
        }

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_add_update_and_refresh_preserves_recruitment_work(self):
        created = add_or_refresh_shortlist_player(
            self.player,
            source_page="Scouting",
            db_path=self.db_path,
        )
        self.assertEqual(created["status"], "Watching")
        self.assertEqual(created["priority"], "Medium")

        updated = update_shortlist_entry(
            "record_1",
            status="Priority",
            priority="Critical",
            target_fee_eur=12_500_000,
            scout_rating=88,
            notes="Strong movement and finishing.",
            db_path=self.db_path,
        )
        self.assertEqual(updated["status"], "Priority")
        self.assertEqual(updated["scout_rating"], 88)

        refreshed_player = dict(self.player)
        refreshed_player["Goals"] = 12
        refreshed = add_or_refresh_shortlist_player(
            refreshed_player,
            source_page="Player Similarity",
            db_path=self.db_path,
        )

        self.assertEqual(len(list_shortlist_entries(db_path=self.db_path)), 1)
        self.assertEqual(refreshed["status"], "Priority")
        self.assertEqual(refreshed["priority"], "Critical")
        self.assertEqual(refreshed["notes"], "Strong movement and finishing.")
        self.assertEqual(json.loads(refreshed["snapshot_json"])["Goals"], 12)
        self.assertEqual(refreshed["source_page"], "Player Similarity")

    def test_filters_and_removal(self):
        add_or_refresh_shortlist_player(self.player, db_path=self.db_path)
        second_player = dict(self.player)
        second_player.update(
            {
                "Player Record ID": "record_2",
                "Player Name": "Test Defender",
                "Position": "DF",
            }
        )
        add_or_refresh_shortlist_player(second_player, db_path=self.db_path)
        update_shortlist_entry(
            "record_2",
            status="Scouted",
            priority="High",
            db_path=self.db_path,
        )

        filtered = list_shortlist_entries(
            statuses=["Scouted"],
            priorities=["High"],
            db_path=self.db_path,
        )
        self.assertEqual([entry["player_record_id"] for entry in filtered], ["record_2"])
        self.assertTrue(remove_shortlist_entry("record_1", db_path=self.db_path))
        self.assertFalse(remove_shortlist_entry("missing", db_path=self.db_path))
        with self.assertRaises(KeyError):
            get_shortlist_entry("record_1", db_path=self.db_path)

    def test_invalid_workflow_values_are_rejected(self):
        add_or_refresh_shortlist_player(self.player, db_path=self.db_path)
        with self.assertRaises(ValueError):
            update_shortlist_entry(
                "record_1",
                status="Signed",
                priority="High",
                db_path=self.db_path,
            )
        with self.assertRaises(ValueError):
            update_shortlist_entry(
                "record_1",
                status="Watching",
                priority="High",
                scout_rating=101,
                db_path=self.db_path,
            )

    def test_database_file_is_released_after_each_operation(self):
        add_or_refresh_shortlist_player(self.player, db_path=self.db_path)
        list_shortlist_entries(db_path=self.db_path)

        renamed_path = self.db_path.with_name("shortlist-renamed.sqlite3")
        self.db_path.replace(renamed_path)
        renamed_path.replace(self.db_path)
        self.assertTrue(self.db_path.is_file())


if __name__ == "__main__":
    unittest.main()
