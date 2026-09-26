"""Read-only teaching helpers. No model downloads or flight connections."""
import argparse
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import shutil
import sys


def doctor():
    packages = {}
    for name in ("numpy", "Pillow", "torch", "lerobot", "mavsdk"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {
        "python": platform.python_version(), "executable": sys.executable,
        "platform": platform.system(), "architecture": platform.machine(),
        "working_directory": str(Path.cwd()), "packages": packages,
        "free_disk_gib": round(shutil.disk_usage(Path.cwd()).free / 2**30, 1),
        "in_virtual_environment": sys.prefix != sys.base_prefix,
        "note": "Package presence does not verify CUDA, MPS, Gazebo or flight readiness.",
    }


def episode(path):
    import numpy as np
    rows = [json.loads(line) for line in (Path(path) / "steps.jsonl").read_text().splitlines()]
    if not rows:
        raise ValueError("Episode has no steps")
    first = rows[0]
    anchor = np.asarray(first["position_ned_m"][:2], dtype=float)
    action = np.asarray(first["action_delta_ne_m"], dtype=float)
    accepted = np.asarray(first["accepted_position_ne_m"], dtype=float)
    next_position = rows[1]["position_ned_m"][:2] if len(rows) > 1 else None
    return {
        "steps": len(rows), "instruction": first["instruction"],
        "first_capture_time_s": first["capture_time_s"],
        "capture_anchor_ne_m": anchor.tolist(), "action_delta_ne_m": action.tolist(),
        "action_length_m": float(np.linalg.norm(action)),
        "anchor_plus_action_ne_m": (anchor + action).tolist(),
        "accepted_position_ne_m": accepted.tolist(),
        "anchor_plus_action_matches": bool(np.allclose(anchor + action, accepted)),
        "next_measured_position_ne_m": next_position,
        "note": "A boundary-clipped target can differ from anchor plus action. A setpoint is not a measured position.",
    }


def training(path):
    history = json.loads((Path(path) / "history.json").read_text())
    if not history:
        raise ValueError("Training history is empty")
    key = "val_mse_normalised"
    if any(not math.isfinite(row[key]) for row in history):
        raise ValueError("Non-finite validation loss")
    best = min(history, key=lambda row: row[key])
    return {"epochs_recorded": len(history), "first": history[0], "last": history[-1],
            "selected_epoch": best["epoch"], "best_validation_mse_normalised": best[key],
            "note": "This describes the NumPy learner. Action loss alone does not measure navigation success."}


def compare(paths):
    reports = []
    for path in paths:
        folder = Path(path)
        summary = json.loads((folder / "summary.json").read_text())
        trials = json.loads((folder / "trials.json").read_text())
        if not trials:
            raise ValueError(f"No trials in {folder}")
        starts = [(row["seed"], row.get("target", row.get("requested_target"))) for row in trials]
        if reports and starts != reference_starts:
            raise ValueError("Runs must use the same ordered seeds and requested targets")
        if not reports:
            reference_starts = starts
            reference_split = summary.get("split", "unrecorded")
        if summary.get("split", "unrecorded") != reference_split:
            raise ValueError("Runs must use the same recorded split")
        successes = sum(bool(row["success"]) for row in trials)
        if summary["episodes"] != len(trials) or summary["success_count"] != successes:
            raise ValueError(f"Summary disagrees with trials in {folder}")
        reports.append({"run": str(folder), "successes": successes, "episodes": len(trials),
                        "success_rate": successes / len(trials),
                        "language": summary.get("language_condition", summary.get("language")),
                        "failed_trials": [{"seed": row["seed"],
                                           "target": row.get("target", row.get("requested_target"))}
                                          for row in trials if not row["success"]]})
    return {"split": reference_split, "runs": reports,
            "note": "Compare failure causes as well as counts. Historical summaries may omit the split."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor")
    for name in ("episode", "training"):
        command = commands.add_parser(name)
        command.add_argument("path", type=Path)
    command = commands.add_parser("compare")
    command.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    if args.command == "doctor": result = doctor()
    elif args.command == "episode": result = episode(args.path)
    elif args.command == "training": result = training(args.path)
    else: result = compare(args.paths)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
