import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np

from integration.data import validate
from litterlab.__main__ import collect, rollout
from litterlab.learning import train


KIT = Path(__file__).resolve().parents[1]


def command(*args):
    return subprocess.run(
        [sys.executable, *args], cwd=KIT, capture_output=True, text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False,
    )


class EvaluationTests(unittest.TestCase):
    def test_cli_selects_validation_by_default_and_explicit_test_scenes(self):
        with tempfile.TemporaryDirectory() as directory:
            for split, options, seed in [("val", [], 100000),
                                         ("test", ["--split", "test"], 200000)]:
                with self.subTest(split=split):
                    out = Path(directory) / split
                    result = command("-m", "litterlab", "evaluate", "--episodes", "1",
                                     "--out", str(out), *options)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    summary = json.loads((out / "summary.json").read_text())
                    trials = json.loads((out / "trials.json").read_text())
                    self.assertEqual(summary["split"], split)
                    self.assertEqual(trials[0]["seed"], seed)
                    self.assertEqual(trials[0]["target"], "bottle")
                    self.assertEqual(trials[0]["input_task"], "centre above the bottle")

    def test_classical_interventions_are_rejected_before_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            for language in ("swapped", "empty"):
                with self.subTest(language=language):
                    out = Path(directory) / language
                    result = command("-m", "litterlab", "evaluate", "--language", language,
                                     "--out", str(out))
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("requires --model", result.stderr)
                    self.assertFalse(out.exists())
                    with self.assertRaisesRegex(ValueError, "require a learned model"):
                        rollout(7, 1, language=language)

    def test_learned_interventions_record_actual_input_and_keep_original_goal(self):
        class RecordingPolicy:
            def __init__(self): self.inputs = []
            def action(self, features):
                self.inputs.append(features)
                return np.zeros(2)

        for language, expected_task, encoding in [
            ("swapped", "centre above the paper", [0, 0, 1]),
            ("empty", "", [0, 0, 0]),
        ]:
            with self.subTest(language=language):
                model = RecordingPolicy()
                env, steps, _, success = rollout(7, 1, model=model, language=language)
                self.assertTrue(all(row["instruction"] == expected_task for row in steps))
                for features in model.inputs:
                    np.testing.assert_array_equal(features[9:12], encoding)
                self.assertFalse(success)
                self.assertFalse(env.success(1))


class DatasetValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.root = Path(cls.directory.name) / "data"
        with contextlib.redirect_stdout(io.StringIO()):
            collect(SimpleNamespace(out=cls.root, train=1, val=1, test=1))
        with np.load(cls.root / "samples.npz", allow_pickle=False) as data:
            cls.original = {key: data[key].copy() for key in data.files}

    def setUp(self):
        self.cache = {key: value.copy() for key, value in self.original.items()}
        self.write_cache()

    def write_cache(self):
        np.savez(self.root / "samples.npz", **self.cache)

    def test_collected_dataset_validates_and_trains(self):
        counts = validate(self.root)
        self.assertEqual(sum(counts.values()), len(self.cache["x"]))
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "model"
            result = train(self.root, out, epochs=1)
            self.assertTrue(np.isfinite(result["best_validation_mse_normalised"]))
            self.assertTrue((out / "policy.npz").is_file())

    def test_missing_corrupt_or_incomplete_cache_is_rejected(self):
        for case in ("missing", "corrupt", "incomplete"):
            with self.subTest(case=case):
                self.write_cache()
                path = self.root / "samples.npz"
                if case == "missing": path.unlink()
                elif case == "corrupt": path.write_bytes(b"not a NumPy archive")
                else: np.savez(path, x=self.cache["x"])
                with self.assertRaisesRegex(ValueError, "Cannot read training cache"):
                    validate(self.root)

    def test_mismatched_features_actions_splits_and_ids_are_rejected(self):
        for key in ("x", "y", "split", "episode_id"):
            with self.subTest(key=key):
                self.cache = {name: value.copy() for name, value in self.original.items()}
                if key in ("x", "y"): self.cache[key][0, 0] += .01
                elif key == "split": self.cache[key][0] = "val"
                else: self.cache[key][0] = "val_0000"
                self.write_cache()
                with self.assertRaisesRegex(ValueError, "samples.npz"):
                    validate(self.root)

    def test_invalid_shapes_and_nonfinite_values_are_rejected(self):
        for case in ("shape", "nan"):
            with self.subTest(case=case):
                self.cache = {key: value.copy() for key, value in self.original.items()}
                if case == "shape": self.cache["x"] = self.cache["x"][:, :13]
                else: self.cache["y"][0, 0] = np.nan
                self.write_cache()
                with self.assertRaisesRegex(ValueError, "samples.npz"):
                    validate(self.root)

    def test_training_rejects_stale_cache_before_creating_output(self):
        self.cache["x"][0, 0] += .01
        self.write_cache()
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "model"
            with self.assertRaisesRegex(ValueError, "disagrees with source records"):
                train(self.root, out, epochs=1)
            self.assertFalse(out.exists())

    def test_validation_remains_active_with_python_optimisation(self):
        path = self.root / "train_0000" / "steps.jsonl"
        original = path.read_text()
        rows = [json.loads(line) for line in original.splitlines()]
        rows[0]["action_delta_ne_m"] = [5., 0.]
        try:
            path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
            result = command("-O", "-m", "integration.data", "--data", str(self.root))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Action exceeds bound", result.stderr)
        finally:
            path.write_text(original)


if __name__ == "__main__":
    unittest.main()
