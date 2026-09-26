"""Unexecuted GPU closed-loop evaluation exercise for the adapted checkpoint."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
from .data import STATE_SCALE, ACTION_SCALE
from litterlab.core import Field, CATEGORIES, HEIGHT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--split", choices=["val", "test"], default="val")
    ap.add_argument("--language", choices=["normal", "swapped", "empty"], default="normal")
    ap.add_argument("--episodes", type=int, default=30)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.episodes < 1: ap.error("episodes must be positive")
    out = Path(args.out); out.mkdir(parents=True, exist_ok=False)
    import torch
    from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
    from lerobot.policies.factory import make_pre_post_processors
    policy = SmolVLAPolicy.from_pretrained(args.checkpoint).to("cuda").eval()
    pre, post = make_pre_post_processors(policy.config, pretrained_path=args.checkpoint)
    trials = []; latency = []
    for i in range(args.episodes):
        env = Field((100000 if args.split == "val" else 200000) + i)
        target = i % 3; instruction_target = target if args.language == "normal" else (target + 1) % 3
        task = "" if args.language == "empty" else f"centre above the {CATEGORIES[instruction_target]}"
        policy.reset(); pre.reset(); post.reset(); dwell = 0
        for step in range(60):
            obs = env.observe()
            state = np.array([*obs.velocity, HEIGHT, 0., 0., 0., 1.], dtype=np.float32) / STATE_SCALE
            pixels = np.array(obs.image, dtype=np.float32).transpose(2, 0, 1) / 255.
            raw = {"observation.images.overhead": torch.from_numpy(pixels)[None],
                   "observation.state": torch.from_numpy(state)[None], "task": [task]}
            torch.cuda.synchronize(); start = time.perf_counter()
            with torch.no_grad(): action = post(policy.select_action(pre(raw)))
            torch.cuda.synchronize(); latency.append(time.perf_counter() - start)
            delta = action.detach().cpu().numpy().reshape(-1) * ACTION_SCALE
            env.apply(delta)
            dwell = dwell + 1 if env.success(target) else 0
            if dwell >= 2: break
        trials.append({"seed": (100000 if args.split == "val" else 200000) + i,
                       "requested_target": CATEGORIES[target], "input_task": task,
                       "success": dwell >= 2, "sim_seconds": env.time})
    report = {"domain": "toy simulator; GPU inference does not advance simulation time",
              "success_count": sum(x["success"] for x in trials), "episodes": len(trials),
              "split": args.split, "language": args.language,
              "inference_seconds_p50_p95": np.quantile(latency, [.5, .95]).tolist(),
              "latency_note": "includes cold calls; not the deployment benchmark"}
    (out / "summary.json").write_text(json.dumps(report, indent=2))
    (out / "trials.json").write_text(json.dumps(trials, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__": main()
