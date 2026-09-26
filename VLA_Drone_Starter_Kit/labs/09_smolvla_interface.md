# Lab 9 Verify the SmolVLA interface

**Where:** CUDA workstation for runtime; Mac for data preparation. **Before starting:** Labs 3–5. **Theory:** guide pages 49–51. **Status:** movement integration supplied; GPU smoke test pending.

## Goal

Make one pretrained movement model consume the documented image, instruction and state, then save and reload a usable drone action interface. This lab does not implement mission-event or semantic heads.

## Predict before setup

On your Mac, inspect one training sample with `integration.data.records`. Write its seven state values and two action values with units. Explain how raw RGB differs from the tiny learner's colour features. Predict each tensor's shape and range before checking the table below.

| Tensor | Shape before model padding | Range or scaling |
| --- | --- | --- |
| RGB | B × 3 × 96 × 96 | Float pixels divided by 255 |
| State | B × 7 | Divide by [1, 1, 5, 1, 1, 1, 1] |
| Action label | B × 1 × 2 | North/east metres divided by 0.5 |

The internal 32-dimensional padding belongs to the pretrained implementation. Confirm how the pinned model handles padded action dimensions and loss; record any change before comparing runs.

## Set up the CUDA environment

Use a separate Python environment compatible with the pinned LeRobot release. The CPU lab's Python 3.14 verification does not establish compatibility with the GPU stack. Have the lab provide the CUDA-compatible PyTorch build. Then follow `docs/SMOLVLA.md`:

```sh
python -m pip install \
  'lerobot[smolvla] @ git+https://github.com/huggingface/lerobot.git@v0.4.4'
python -m pip install -r requirements.txt
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
nvidia-smi
python -m integration.data --data runs/lab03-data
```

Copy the complete dataset to the workstation at that path, or use its local equivalent consistently. The first policy load can download pretrained weights. Record the resolved model revision and LeRobot commit, not just their names.

## Run the smallest useful smoke test

```sh
python -m integration.train_smolvla --data runs/lab03-data \
  --out runs/lab09-smoke --steps 1 --batch-size 1
python -m integration.evaluate_smolvla \
  --checkpoint runs/lab09-smoke/best --split val \
  --episodes 1 --out runs/lab09-reload
```

Even a one-step run evaluates the full validation loader. Record the first tensor shapes, finite loss, nonzero trainable gradient norm and names of trainable/reinitialized layers using temporary diagnostic logging. Confirm saved processors exist. Reloading for one rollout must produce two finite action components after postprocessing. Failure to navigate after one update is not an interface failure.

## Apple GPU status

The supplied trainer and evaluator explicitly use CUDA. Setting an environment variable will not convert them to MPS. A future Mac port must change device selection, processors, synchronization and validation RNG handling, then pass the same gradient/reload checks. No local MPS training result is claimed here.

## Completion check and troubleshooting

Save the environment, tensor/gradient record, one-step history, checkpoint and reload result. Import errors require checking the pinned environment. Shape errors require checking the action time dimension. Memory errors start with batch size one. Do not launch longer training until this milestone passes.
