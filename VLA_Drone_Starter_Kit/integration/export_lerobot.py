"""Optional local LeRobot v0.4.4 export. Not executed in the author environment."""
import argparse
from pathlib import Path
import numpy as np
from PIL import Image
from .data import records, validate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--split", choices=["train", "val", "test"], required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    validate(args.data)
    if Path(args.out).exists():
        raise FileExistsError(args.out)
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    features = {
        "observation.images.overhead": {"dtype": "image", "shape": (96, 96, 3),
                                        "names": ["height", "width", "channels"]},
        "observation.state": {"dtype": "float32", "shape": (7,),
                              "names": ["v_n", "v_e", "height", "roll", "pitch", "sin_yaw", "cos_yaw"]},
        "action": {"dtype": "float32", "shape": (2,), "names": ["delta_n", "delta_e"]},
    }
    dataset = LeRobotDataset.create(repo_id=f"local/litter_{args.split}", fps=2,
                features=features, root=Path(args.out), robot_type="drone_position_demo", use_videos=False)
    current = None
    for row in records(args.data, args.split):
        if current is not None and row["episode_id"] != current:
            dataset.save_episode()
        current = row["episode_id"]
        dataset.add_frame({"observation.images.overhead": np.array(Image.open(row["image"]).convert("RGB")),
                           "observation.state": row["state"], "action": row["action"], "task": row["task"]})
    if current is not None:
        dataset.save_episode()
    dataset.finalize()
    print(f"Saved {args.split} locally at {args.out}; nothing uploaded.")


if __name__ == "__main__":
    main()
