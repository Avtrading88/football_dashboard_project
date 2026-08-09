import unittest

import pandas as pd

from src.feature_engineering import add_derived_metrics, add_player_identity_columns
from src.player_scouting import (
    calculate_player_scores,
    calculate_role_percentile_scores,
)


class FeatureEngineeringTests(unittest.TestCase):
    def setUp(self):
        self.players = pd.DataFrame(
            {
                "Player Name": ["Transfer Player", "Transfer Player", "Forward Two", "Defender One"],
                "Birth Year": [2000, 2000, 1999, 1998],
                "Nationality": ["England", "England", "France", "Germany"],
                "Position": ["FW", "FW", "FW", "DF"],
                "Club": ["Club A", "Club B", "Club C", "Club D"],
                "League": ["League 1", "League 2", "League 1", "League 1"],
                "Age": [26, 26, 27, 28],
                "Minutes Played": [900, 900, 900, 900],
                "Matches Played": [10, 10, 10, 10],
                "Goals": [10, 5, 2, 0],
                "Non-Penalty Goals": [9, 5, 2, 0],
                "Assists": [2, 3, 5, 1],
                "Goals + Assists": [12, 8, 7, 1],
                "Shots": [40, 30, 20, 5],
                "Shots on Target": [20, 15, 8, 1],
                "Shots on Target Percentage": [50, 50, 40, 20],
                "Goals per Shot": [0.225, 0.167, 0.1, 0.0],
                "Crosses": [5, 8, 20, 15],
                "Tackles Won": [2, 3, 8, 30],
                "Interceptions": [1, 2, 5, 25],
                "Fouled": [10, 8, 12, 5],
                "Fouls Committed": [4, 5, 8, 10],
                "Yellow Cards": [1, 1, 2, 3],
                "Red Cards": [0, 0, 0, 0],
            }
        )

    def test_transfer_records_share_player_id_but_not_record_id(self):
        result = add_player_identity_columns(self.players)
        first, second = result.iloc[0], result.iloc[1]
        self.assertEqual(first["Player ID"], second["Player ID"])
        self.assertNotEqual(first["Player Record ID"], second["Player Record ID"])
        self.assertEqual(result["Player Record ID"].nunique(), len(result))

    def test_per_90_and_defensive_metrics(self):
        result = add_derived_metrics(self.players)
        self.assertAlmostEqual(result.loc[0, "Goals per 90"], 1.0)
        self.assertAlmostEqual(result.loc[3, "Defensive Actions per 90"], 5.5)
        self.assertAlmostEqual(result.loc[0, "Goal Conversion Percentage"], 22.5)

    def test_custom_score_rebalances_unavailable_optional_metrics(self):
        result = calculate_player_scores(self.players, min_minutes=0)
        self.assertIsNotNone(result)
        self.assertTrue(result["Player Score"].between(0, 100).all())
        self.assertEqual(result["Score Coverage %"].unique().tolist(), [60.0])
        self.assertEqual(result["Score Components Used"].unique().tolist(), ["goals, assists"])

    def test_role_scores_are_position_relative_and_bounded(self):
        result = calculate_role_percentile_scores(self.players, min_minutes=0)
        self.assertIsNotNone(result)
        self.assertTrue(result["Role Score"].between(0, 100).all())
        self.assertSetEqual(set(result["Primary Position"]), {"FW", "DF"})


if __name__ == "__main__":
    unittest.main()
