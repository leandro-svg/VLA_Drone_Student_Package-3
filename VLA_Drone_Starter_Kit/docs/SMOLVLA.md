# SmolVLA GPU lab

Follow the expanded [Lab 9](../labs/09_smolvla_interface.md) for a one-step and reload check before the longer [Lab 10](../labs/10_smolvla_training.md). The CPU lab environment and Python version do not establish LeRobot compatibility. The current scripts explicitly require CUDA; Apple MPS adaptation remains a separate, unverified task.

**Scope: movement pilot only.** This trainer does not implement the final mission-event, grounding or semantic heads. See [SINGLE_VLA.md](SINGLE_VLA.md) and Labs 11–12 for the research implementation.


**Status: supplied integration code, source-reviewed against LeRobot v0.4.4, syntax checked, NOT executed with PyTorch, model weights or a GPU here.** The supervisor must run the smoke test with the student before treating this as a supported lab environment.

Use an isolated Python 3.10+ environment on the lab CUDA workstation. Have the lab install a CUDA-compatible PyTorch build first. Do not perform training on the Orin as the default plan.

```sh
python3 -m venv .venv-vla
source .venv-vla/bin/activate
python -m pip install 'lerobot[smolvla] @ git+https://github.com/huggingface/lerobot.git@v0.4.4'
python -m pip install -r requirements.txt
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
python -m integration.train_smolvla --data runs/data --out runs/vla-smoke --steps 100 --batch-size 2
```

Run commands from the starter-kit root. First use may download pretrained weights and a tokenizer. Save `python -m pip freeze` and `nvidia-smi` output in the run directory. Record the resolved LeRobot and model revisions; the tag is a candidate integration pin, not a claim that this hardware stack has been tested.

## Exact model interface

Input: full RGB frame, instruction string and seven state entries in this order: north velocity, east velocity, height, roll, pitch, sine of yaw, cosine of yaw. SI units, except the sine/cosine. Divide state by `[1,1,5,1,1,1,1]`. Divide two-dimensional `[delta_n,delta_e]` labels in metres by `0.5`. Keep the pretrained 32-dimensional padding; only the first two output values describe the task. Predict one action at a time. These fixed scales avoid importing robot-arm normalisation statistics; training data statistics are not needed for this deliberately simple contract.

The script loads `lerobot/smolvla_base`, replaces feature specifications, resets state and action input/output projections, creates fresh processors and calls the policy's native flow-matching loss. It retains the pretrained representation and action expert as a starting point. This is a transfer-learning hypothesis, not evidence that an arm-trained model already flies.

The first GPU pass must confirm: image batch `B×3×96×96`, state `B×7`, labels `B×1×2`, finite loss, nonzero trainable gradients, saved processors, and two finite outputs after reload. The images are resized inside SmolVLA; this cannot recover detail missing from the original 96-pixel image.

For a longer development run, start a new output directory:

```sh
python -m integration.train_smolvla --data runs/data --out runs/vla-dev --steps 2000 --batch-size 2
python -m integration.evaluate_smolvla --checkpoint runs/vla-dev/best --split val --out runs/vla-val
```

The script chooses a checkpoint using validation flow loss. Inspect validation closed-loop performance too; a lower training loss is not a navigation result. Once the protocol and checkpoint are frozen:

```sh
python -m integration.evaluate_smolvla --checkpoint runs/vla-dev/best --split test --out runs/vla-test
python -m integration.evaluate_smolvla --checkpoint runs/vla-dev/best --split test --language swapped --out runs/vla-swap
```

This evaluator pauses the toy world while inference runs. Its success rate therefore ignores delay-induced control error. Inference latency is logged separately, including cold calls; use the complete guide's Orin benchmark on page 60 for deployment claims.

Optional LeRobot interchange format, independently of the supplied raw-frame training loop:

```sh
python -m integration.export_lerobot --data runs/data --split train --out runs/lerobot-train
```

Repeat with separate destinations for validation and test. No data is uploaded. Do not merge splits and recompute statistics on all of them.

## If the smoke test fails

- Import error: confirm the exact tag and active environment; do not silently switch to the latest branch.
- Shape error: print the three tensors above before `policy(batch)`. Preserve action's time dimension even when it equals one.
- Missing statistics: use the fresh identity processors created by this exercise, not the original arm processor files.
- Out of memory: batch size 1 first, then reduce image resolution only after checking object pixel size. Record the changed experiment.
- Non-finite loss: inspect finite state/action values and image range; stop before collecting more episodes.
- Poor validation success: inspect action units, frame signs, stale observations and insufficient task coverage before adding model size.

Sources: [LeRobot v0.4.4](https://github.com/huggingface/lerobot/tree/v0.4.4), [SmolVLA](https://arxiv.org/abs/2506.01844), [base checkpoint](https://huggingface.co/lerobot/smolvla_base).
