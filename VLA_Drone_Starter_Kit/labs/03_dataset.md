# Lab 3 Collect and audit demonstrations

**Where:** Mac CPU. **Before starting:** Lab 2. **Theory:** guide pages 24–25 and 43–48. **Status:** runnable teaching exercise.

## Goal

Trace one supervised learning example from its image to its task, state and action label. Separate deployable inputs from expert-only information and keep related samples in the same split.

## Predict before running

The expert can access exact object positions. The learner receives image-derived features, a requested category and velocity. What would happen to measured performance if the learner were given the target's true coordinates? Why could random frame splitting make a model look better than it is?

## Collect and validate

```sh
python -m litterlab collect --out runs/lab03-data
python -m integration.data --data runs/lab03-data
python -m integration.lab_tools episode runs/lab03-data/train_0000
```

Expected collection: 150 training, 30 validation and 30 test episodes, zero expert failures and 1,569 samples. Validation reports 1,144 training, 210 validation and 215 test samples. Counts refer to the supplied default generator.

## Follow one record

1. Open `train_0000/images/0000.png` and the first row of `steps.jsonl`. Locate the requested category visually and predict the action signs.
2. Identify the seven state values: north velocity, east velocity, height, roll, pitch, sine yaw and cosine yaw. Distinguish this from the 14-element tiny-policy feature vector.
3. Verify that timestamps start at zero and advance by 0.5 s. Each action belongs to the observation recorded on that row.
4. Read `manifest.json`. The seed ranges start at 0, 100000 and 200000 for train, validation and test. Keep entire episodes together.
5. Open `evaluator_only.json` to understand its contents, then inspect the loader in `integration/data.py`: those coordinates must not become policy inputs.

## Deliberately break a copy

Copy `runs/lab03-data` to a fresh scratch directory, change the first action in one training `steps.jsonl` to `[5.0, 0.0]`, and run the validator on the copy. It should reject the bound violation. Restore the scratch copy, change the action slightly within bounds without rebuilding its cache, and confirm the validator detects the disagreement with `samples.npz`. Keep the original dataset intact.

## Completion check

Save the validator output and an annotated record showing the image, task, state and label. Explain why `samples.npz` is a derived cache, why evaluator truth is separate, and why a split seed is only sufficient for this controlled generator. Real missions also need layout, collection-session and physical-item grouping.

## Troubleshooting and extension

A missing or stale cache requires regenerating a complete teaching dataset in a fresh directory. Do not dismiss the error by removing checks. For a quick second dataset, use `--train 3 --val 3 --test 3`; label it a small workflow test and report its actual counts.

