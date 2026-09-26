# Lab 10 Train and evaluate the movement pilot

**Where:** CUDA workstation; Mac for report analysis. **Before starting:** Lab 9 runtime pass. **Theory:** guide pages 52–55. **Status:** training/evaluation scripts supplied; results must be measured.

## Goal

Establish whether the adapted model learns the movement task, select using development evidence and measure behaviour separately from inference latency.

## Predict before running

The toy world pauses during inference. Could a model taking two seconds per decision still succeed in a simulated 2 Hz task? Explain why simulation success does not prove it can meet a 0.5-second wall-clock deadline.

## Train in stages

First run a small development job:

```sh
python -m integration.train_smolvla --data runs/lab03-data \
  --out runs/lab10-short --steps 100 --batch-size 2
python -m integration.evaluate_smolvla \
  --checkpoint runs/lab10-short/best --split val \
  --out runs/lab10-short-val
```

If the interface remains correct and the run fits memory, start a fresh 2,000-step job with `--out runs/lab10-dev`. This is a new run, not a resume of the 100-step optimiser state. Evaluate its `best` checkpoint on validation scenes with the same settings. Do not invent an expected loss or success threshold from the CPU learner's results.

The supplied trainer selects by validation flow loss. Use closed-loop validation to judge whether that selection is useful. Freeze your selection rule before comparing several checkpoints or configurations. A successful tiny overfit experiment can diagnose wiring; it is not a generalisation result.

## Inspect the training bundle

Retain `history.json`, `best/`, processor files and `drone_interface.json`. Also save `python -m pip freeze`, the GPU record, resolved model revision, elapsed time, peak memory, seed and dataset identity. The script does not automatically capture all of these.

Explain which projections were reset, which parameters trained and why the original robot-arm normalisation was replaced. Confirm that a freshly loaded checkpoint produces correctly scaled actions.

## Evaluate the frozen model

```sh
python -m integration.evaluate_smolvla \
  --checkpoint runs/lab10-dev/best --split test \
  --out runs/lab10-test
python -m integration.evaluate_smolvla \
  --checkpoint runs/lab10-dev/best --split test --language swapped \
  --out runs/lab10-swapped
python -m integration.evaluate_smolvla \
  --checkpoint runs/lab10-dev/best --split test --language empty \
  --out runs/lab10-empty
python -m integration.lab_tools compare \
  runs/lab10-test runs/lab10-swapped runs/lab10-empty
```

Compare a classical run on the same split and starts. Record stochastic inference settings; the supplied evaluator does not expose a seed flag, so paired repeated evaluations need an explicitly controlled RNG protocol before research claims about small differences.

## Completion check

Save a reloadable checkpoint, matched outcomes, one failure explanation and p50/p95 inference times. The current timing includes cold calls and excludes simulator motion during inference. Report it as an offline timing diagnostic. Device deployment needs a separate real-time experiment. Multiple training seeds are a research extension; report the number actually run.

## Troubleshooting

For weak performance, inspect scaling, image content, labels and trainable parameters before increasing model size. If GPU access is unavailable, complete the comparison-table design and mark training pending; CPU teaching weights cannot substitute for SmolVLA evidence.

