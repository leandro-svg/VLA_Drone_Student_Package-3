import json
from pathlib import Path
import tempfile
import unittest

from integration.lab_tools import compare, episode, training


class LabToolsTests(unittest.TestCase):
    def test_episode_distinguishes_command_from_next_measurement(self):
        with tempfile.TemporaryDirectory() as directory:
            rows = [{"instruction": "centre above the can", "capture_time_s": 0,
                     "position_ned_m": [1, 2, -5], "action_delta_ne_m": [.3, .4],
                     "accepted_position_ne_m": [1.3, 2.4]},
                    {"position_ned_m": [1.1, 2.1, -5]}]
            (Path(directory) / "steps.jsonl").write_text("\n".join(map(json.dumps, rows)))
            report = episode(directory)
            self.assertTrue(report["anchor_plus_action_matches"])
            self.assertAlmostEqual(report["action_length_m"], .5)
            self.assertNotEqual(report["accepted_position_ne_m"], report["next_measured_position_ne_m"])

    def test_training_uses_best_validation_epoch_including_ties(self):
        with tempfile.TemporaryDirectory() as directory:
            rows = [{"epoch": i + 1, "val_mse_normalised": loss}
                    for i, loss in enumerate([.3, .1, .1, .2])]
            (Path(directory) / "history.json").write_text(json.dumps(rows))
            self.assertEqual(training(directory)["selected_epoch"], 2)

    def test_compare_rejects_different_scenes_and_inconsistent_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / name for name in ("a", "b")]
            for path in paths:
                path.mkdir()
                (path / "summary.json").write_text(json.dumps({"split": "val", "episodes": 1, "success_count": 0}))
                (path / "trials.json").write_text(json.dumps([{"seed": 100000, "target": "can", "success": False}]))
            report = compare(paths)
            self.assertEqual(report["runs"][0]["failed_trials"], [{"seed": 100000, "target": "can"}])
            (paths[1] / "trials.json").write_text(json.dumps([{"seed": 200000, "target": "can", "success": False}]))
            with self.assertRaisesRegex(ValueError, "same ordered seeds"):
                compare(paths)
            (paths[0] / "summary.json").write_text(json.dumps({"split": "val", "episodes": 1, "success_count": 1}))
            with self.assertRaisesRegex(ValueError, "disagrees"):
                compare([paths[0]])


if __name__ == "__main__":
    unittest.main()
