import sys
import types
import unittest


try:
    import streamlit  # noqa: F401
except ModuleNotFoundError:
    streamlit_stub = types.ModuleType("streamlit")
    streamlit_stub.cache_data = lambda function: function
    sys.modules["streamlit"] = streamlit_stub

from src.data_loader import load_data
from src.league_analysis import create_league_summary
from src.player_similarity import find_similar_players


class DatasetIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.players = load_data()

    def test_bundled_dataset_has_expected_engineered_schema(self):
        required_columns = {
            "Player ID",
            "Player Record ID",
            "Player Selection Label",
            "Shots",
            "Shots on Target per 90",
            "Shot Accuracy Percentage",
            "Tackles Won",
            "Interceptions",
            "Defensive Actions per 90",
            "Save Percentage",
            "Penalty Save Percentage",
        }
        self.assertTrue(required_columns.issubset(self.players.columns))
        self.assertEqual(self.players["Player Record ID"].nunique(), len(self.players))
        self.assertEqual((self.players["Nationality"] == "nan").sum(), 0)

    def test_league_summary_does_not_call_player_appearances_matches(self):
        summary = create_league_summary(self.players)
        self.assertIn("Player Appearances", summary.columns)
        self.assertNotIn("Total Matches Played", summary.columns)
        self.assertIn("Defensive Actions per 90", summary.columns)

    def test_similarity_uses_transfer_safe_record_identity(self):
        transferred = self.players[
            self.players.duplicated("Player ID", keep=False)
        ]
        selected_record = transferred.iloc[0]["Player Record ID"]
        result = find_similar_players(
            self.players,
            selected_record,
            ["Goals per 90", "Shots on Target per 90", "Defensive Actions per 90"],
            top_n=5,
            min_minutes=0,
            same_position_only=True,
        )
        self.assertIsNotNone(result)
        self.assertNotIn(selected_record, result["Player Record ID"].tolist())


if __name__ == "__main__":
    unittest.main()
