# Lab 5 Evaluate behaviour and investigate failures

**Where:** Mac CPU. **Before starting:** Lab 4 checkpoint. **Theory:** guide pages 27–28 and 55. **Status:** runnable teaching exercise.

## Goal

Compare policies on matched starts, keep validation separate from final testing, and explain a failure from a replay. Interpret language interventions within this restricted task.

## Predict before running

Will the learned policy outperform the colour-based controller in a world where colour identifies the target exactly? If you give the model a different requested category but keep the original scoring goal, what should happen to success?

## Run validation comparisons

```sh
python -m litterlab evaluate --split val --out runs/lab05-classical
python -m litterlab evaluate --split val \
  --model runs/lab04-tiny/policy.npz --out runs/lab05-learned
python -m litterlab evaluate --split val --language swapped \
  --model runs/lab04-tiny/policy.npz --out runs/lab05-swapped
python -m litterlab evaluate --split val --language empty \
  --model runs/lab04-tiny/policy.npz --out runs/lab05-empty
python -m integration.lab_tools compare \
  runs/lab05-classical runs/lab05-learned \
  runs/lab05-swapped runs/lab05-empty
```

The helper rejects mismatched ordered seeds or requested targets. It lists failed trials for replay. Validation results need not equal the guide's historical test results.

## Diagnose rather than guess

Choose a failed validation trial from the helper output. Substitute its integer seed and category in this command; `SEED` and `CATEGORY` are placeholders:

```sh
python -m litterlab demo --model runs/lab04-tiny/policy.npz \
  --seed SEED --target CATEGORY --out runs/lab05-failure
```

This demo replays the normal-instruction policy. It does not reproduce a swapped/empty trial. Use a failure from the normal learned run for this exercise. If that run has no failures, inspect its worst final error and explain why it still passed.

Compare the image, proposed action, accepted target and trajectory. Classify the observed cause: wrong direction, oscillation, final error, excessive speed or timeout. Success requires being within 0.20 m and below 0.18 m/s for two successive decision ticks, within 60 steps.

## Change dynamics on validation scenes

Repeat the normal learned evaluation with `--response 2` in a fresh folder. This changes the simulator's velocity-response time constant. It does not inject camera or inference latency. Keep seeds fixed and explain any changed failures.

## Final testing after the protocol is frozen

Repeat the four evaluation commands with `--split test` and fresh folders. The supplied seed-0 reference checkpoint yields 30/30 classical, 24/30 learned, 0/30 swapped and 0/30 empty on the original 30 test scenes. These are reference results, not expected validation scores or general language-understanding evidence.

Once test failures inform a model change, that test set is no longer untouched. Develop against validation and reserve a new test set for later research claims.

## Completion check

Save paired summaries, trial records and one normal-policy failure analysis. Explain why changed-task failure can be consistent with following the changed task. Report the sample size and training-seed count. A single 30-scene run does not measure training variability.

