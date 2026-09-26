"""Read public observation/action fields only. No evaluator truth is loaded."""
import json
from pathlib import Path
from zipfile import BadZipFile
import numpy as np
from PIL import Image
from litterlab.core import Observation, parse_instruction, policy_features

STATE_SCALE = np.array([1., 1., 5., 1., 1., 1., 1.], dtype=np.float32)
ACTION_SCALE = 0.5


def records(root, split):
    root = Path(root)
    manifest = json.loads((root / "manifest.json").read_text())
    if manifest["fps"] != 2 or manifest["action_schema"] != "delta_NE_metres_capture_anchor":
        raise ValueError("Expected the supplied 2 Hz position-increment schema")
    for episode in manifest["episodes"]:
        if episode["split"] != split:
            continue
        folder = root / episode["episode_id"]
        for line in (folder / "steps.jsonl").read_text().splitlines():
            row = json.loads(line)
            yield {"image": folder / "images" / row["frame"],
                   "state": np.array(row["state"], dtype=np.float32),
                   "action": np.array(row["action_delta_ne_m"], dtype=np.float32),
                   "task": row["instruction"], "episode_id": episode["episode_id"],
                   "time": row["capture_time_s"]}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_cache(root, expected):
    """Check the tiny trainer's cache against the public source records."""
    path = Path(root) / "samples.npz"
    try:
        with np.load(path, allow_pickle=False) as data:
            arrays = {key: data[key] for key in ("x", "y", "split", "episode_id")}
    except (OSError, ValueError, KeyError, BadZipFile) as exc:
        raise ValueError(f"Cannot read training cache {path}: {exc}") from exc
    size = sum(len(rows) for rows in expected.values())
    for key, shape in {"x": (size, 14), "y": (size, 2),
                       "split": (size,), "episode_id": (size,)}.items():
        require(arrays[key].shape == shape, f"samples.npz: invalid {key} shape")
    for key in ("x", "y"):
        require(arrays[key].dtype.kind in "fiu", f"samples.npz: {key} must be numeric")
        require(np.isfinite(arrays[key]).all(), f"samples.npz: non-finite {key}")
    require(np.isin(arrays["split"], list(expected)).all(), "samples.npz: unknown split")
    for split, rows in expected.items():
        mask = arrays["split"] == split
        require(int(mask.sum()) == len(rows), f"samples.npz: wrong {split} sample count")
        features, actions, episode_ids = zip(*rows)
        require(np.array_equal(arrays["episode_id"][mask], episode_ids),
                f"samples.npz: {split} episode IDs disagree with records")
        for key, values in (("x", features), ("y", actions)):
            require(np.allclose(arrays[key][mask], values, rtol=1e-6, atol=1e-7),
                    f"samples.npz: {split} {key} disagrees with source records")


def validate(root):
    manifest = json.loads((Path(root) / "manifest.json").read_text())
    episodes = manifest["episodes"]
    ids = [e["episode_id"] for e in episodes]
    seeds = [e["seed"] for e in episodes]
    require(len(ids) == len(set(ids)), "Repeated episode ID")
    require(len(seeds) == len(set(seeds)), "A scene seed occurs in multiple episodes")
    require(all(e["split"] in {"train", "val", "test"} for e in episodes), "Unknown episode split")
    counts = {}; expected_cache = {}
    for split in ["train", "val", "test"]:
        previous = {}; count = 0; episode_counts = {}; expected_cache[split] = []
        for row in records(root, split):
            require(row["state"].shape == (7,) and row["action"].shape == (2,), "Invalid state/action shape")
            require(np.isfinite(row["state"]).all() and np.isfinite(row["action"]).all(), "Non-finite state/action")
            require(np.linalg.norm(row["action"]) <= ACTION_SCALE + 1e-6, "Action exceeds bound")
            with Image.open(row["image"]) as im:
                require(im.mode == "RGB" and im.size == (96, 96), "Expected a 96x96 RGB image")
                obs = Observation(im, np.zeros(2), row["state"][:2], row["time"])
                features = policy_features(obs, parse_instruction(row["task"]))
            ep = row["episode_id"]
            expected = previous.get(ep, -0.5) + 0.5
            require(abs(row["time"] - expected) < 1e-6, "Timestamp gap")
            previous[ep] = row["time"]; count += 1
            episode_counts[ep] = episode_counts.get(ep, 0) + 1
            expected_cache[split].append((features, row["action"], ep))
        require(count > 0, f"Empty {split} split")
        for episode in episodes:
            if episode["split"] == split:
                actual = episode_counts.get(episode["episode_id"], 0)
                require(actual > 0 and actual == episode["steps"], "Episode step count disagrees with manifest")
        counts[split] = count
    validate_cache(root, expected_cache)
    return counts


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()
    print(json.dumps({"valid": True, "samples": validate(args.data)}, indent=2))
