"""Concrete GPU adaptation exercise for LeRobot v0.4.4, NOT run here.

Uses raw images and task strings, native SmolVLA flow-matching loss, a new
drone state/action interface and fresh processors. This is not a drone-ready
checkpoint. Requires the GPU smoke test and validation in docs/SMOLVLA.md.
"""
import argparse
import json
from pathlib import Path
import random
import numpy as np
from PIL import Image
from .data import records, validate, STATE_SCALE, ACTION_SCALE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--steps", type=int, default=100)
    ap.add_argument("--batch-size", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    if args.steps < 1 or args.batch_size < 1:
        ap.error("steps and batch size must be positive")
    validate(args.data)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=False)
    import torch
    from torch.utils.data import Dataset, DataLoader
    from lerobot.configs.types import FeatureType, NormalizationMode, PolicyFeature
    from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
    from lerobot.policies.factory import make_pre_post_processors
    if not torch.cuda.is_available():
        raise RuntimeError("Use the lab CUDA workstation for this exercise; the CPU labs need no GPU.")
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    policy = SmolVLAPolicy.from_pretrained("lerobot/smolvla_base")
    cfg = policy.config
    cfg.device = "cuda"
    cfg.chunk_size = 1; cfg.n_action_steps = 1; cfg.n_obs_steps = 1
    cfg.adapt_to_pi_aloha = False; cfg.empty_cameras = 0
    cfg.input_features = {
        "observation.images.overhead": PolicyFeature(type=FeatureType.VISUAL, shape=(3, 96, 96)),
        "observation.state": PolicyFeature(type=FeatureType.STATE, shape=(7,)),
    }
    cfg.output_features = {"action": PolicyFeature(type=FeatureType.ACTION, shape=(2,))}
    # Fixed, documented physical scales are applied by this script, not arm statistics.
    cfg.normalization_mapping = {k: NormalizationMode.IDENTITY for k in ["VISUAL", "STATE", "ACTION"]}
    cfg.train_state_proj = True
    for name in ["state_proj", "action_in_proj", "action_out_proj"]:
        layer = getattr(policy.model, name)
        layer.reset_parameters()
        layer.requires_grad_(True)
    policy.model.set_requires_grad()
    policy.to("cuda"); policy.reset()
    pre, post = make_pre_post_processors(cfg, dataset_stats=None)

    class Frames(Dataset):
        def __init__(self, split): self.rows = list(records(args.data, split))
        def __len__(self): return len(self.rows)
        def __getitem__(self, index):
            row = self.rows[index]
            pixels = np.array(Image.open(row["image"]).convert("RGB"), dtype=np.float32) / 255.
            return {"observation.images.overhead": torch.from_numpy(pixels.transpose(2, 0, 1)),
                    "observation.state": torch.from_numpy(row["state"] / STATE_SCALE),
                    "action": torch.from_numpy((row["action"] / ACTION_SCALE)[None, :]),
                    "task": row["task"]}

    train_loader = DataLoader(Frames("train"), batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(Frames("val"), batch_size=args.batch_size, shuffle=False, num_workers=0)
    optimizer = torch.optim.AdamW([p for p in policy.parameters() if p.requires_grad], lr=1e-4)
    iterator = iter(train_loader); best = float("inf"); history = []
    for step in range(1, args.steps + 1):
        try: batch = next(iterator)
        except StopIteration:
            iterator = iter(train_loader); batch = next(iterator)
        policy.train(); optimizer.zero_grad(set_to_none=True)
        batch = pre(batch)
        assert batch["action"].shape[1:] == (1, 2), batch["action"].shape
        loss, _ = policy(batch)
        if not torch.isfinite(loss): raise RuntimeError("Non-finite training loss")
        loss.backward()
        grad_norm = torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.)
        if not torch.isfinite(grad_norm) or (step == 1 and float(grad_norm) == 0.):
            raise RuntimeError("Non-finite or missing training gradients")
        optimizer.step()
        if step == 1 or step % 100 == 0 or step == args.steps:
            policy.eval(); total = 0.; count = 0
            # Fixed validation RNG gives comparable samples without perturbing training RNG.
            with torch.random.fork_rng(devices=[torch.cuda.current_device()]):
                torch.manual_seed(101)
                with torch.no_grad():
                    for raw in val_loader:
                        b = pre(raw); value, _ = policy(b); n = raw["action"].shape[0]
                        total += float(value) * n; count += n
            score = total / count
            row = {"step": step, "train_flow_loss": float(loss.detach()), "val_flow_loss": score}
            history.append(row); print(json.dumps(row), flush=True)
            (out / "history.json").write_text(json.dumps(history, indent=2))
            if score < best:
                best = score
                checkpoint = out / "best"
                policy.save_pretrained(checkpoint)
                pre.save_pretrained(checkpoint); post.save_pretrained(checkpoint)
    (out / "drone_interface.json").write_text(json.dumps({
        "state_order": ["v_n", "v_e", "height", "roll", "pitch", "sin_yaw", "cos_yaw"],
        "state_scale": STATE_SCALE.tolist(), "action_scale_m": ACTION_SCALE,
        "action_order": ["delta_n", "delta_e"], "rate_hz": 2,
        "anchor": "image capture pose, applied once", "lerobot_tag": "v0.4.4",
        "training": vars(args), "best_validation_flow_loss": best}, indent=2))
    print("GPU training ended. This does NOT establish closed-loop success or flight readiness.")


if __name__ == "__main__": main()
