import json
import unittest

from src.scouting_exports import (
    build_scouting_report_pdf,
    prepare_shortlist_export_dataframe,
    shortlist_to_csv_bytes,
)


class ScoutingExportTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            {
                "player_record_id": "record_1",
                "player_name": "Marek Scouting",
                "nationality": "Poland",
                "position": "MF",
                "club": "Analytics FC",
                "league": "Bundesliga",
                "age": 22,
                "status": "Priority",
                "priority": "Critical",
                "target_fee_eur": 9_500_000,
                "scout_rating": 91,
                "notes": "Creative midfielder. Review defensive transition work.",
                "source_page": "Scouting",
                "created_at": "2026-08-09T12:00:00+00:00",
                "updated_at": "2026-08-09T12:30:00+00:00",
                "snapshot_json": json.dumps(
                    {
                        "Minutes Played": 1900,
                        "Goals": 7,
                        "Assists": 11,
                        "Goals per 90": 0.33,
                        "Assists per 90": 0.52,
                        "Defensive Actions per 90": 3.4,
                    }
                ),
            }
        ]

    def test_export_dataframe_flattens_snapshot_metrics(self):
        dataframe = prepare_shortlist_export_dataframe(self.entries)
        self.assertEqual(dataframe.loc[0, "Player Name"], "Marek Scouting")
        self.assertEqual(dataframe.loc[0, "Status"], "Priority")
        self.assertEqual(dataframe.loc[0, "Assists"], 11)
        self.assertEqual(dataframe.loc[0, "Defensive Actions per 90"], 3.4)

    def test_csv_is_excel_friendly_utf8(self):
        csv_bytes = shortlist_to_csv_bytes(self.entries)
        self.assertTrue(csv_bytes.startswith(b"\xef\xbb\xbf"))
        csv_text = csv_bytes.decode("utf-8-sig")
        self.assertIn("Marek Scouting", csv_text)
        self.assertIn("Target Fee EUR", csv_text)

    def test_pdf_report_is_created(self):
        pdf_bytes = build_scouting_report_pdf(self.entries)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 4_000)

    def test_pdf_requires_at_least_one_candidate(self):
        with self.assertRaises(ValueError):
            build_scouting_report_pdf([])


if __name__ == "__main__":
    unittest.main()

