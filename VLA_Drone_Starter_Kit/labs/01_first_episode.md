# Lab 1 Run and explain your first episode

**Where:** Mac CPU. **Before starting:** complete the workbook environment setup. **Theory:** original guide pages 5–12 and 22. **Status:** runnable teaching exercise.

## Goal

Recognise the loop: acquire an image, choose a horizontal movement, turn it into an absolute position target, simulate motion, then acquire another image. Identify which files contain observations, commands and results.

## Predict before running

Blue represents the can, red the bottle and yellow the paper. With the field held fixed, should a different requested category change the image at the start, the first movement, both, or neither? Write your prediction before comparing the three runs.

## Run the experiment

```sh
python -m unittest discover -s tests -v
python -m litterlab demo --seed 7 --target can --out runs/lab01-can
python -m litterlab demo --seed 7 --target bottle --out runs/lab01-bottle
python -m litterlab demo --seed 7 --target paper --out runs/lab01-paper
python -m integration.lab_tools episode runs/lab01-can
```

On macOS, open the replay and trajectory:

```sh
open runs/lab01-can/replay.gif
open runs/lab01-can/trajectory.png
```

If your viewer shows only one GIF frame, use a browser or an animation-capable viewer. The per-step PNGs are also in `frames/`.

## Inspect the evidence

1. Read `result.json`. The can run should succeed in nine steps and 4.5 simulated seconds with the default dynamics.
2. Compare `frames/0000.png` across all three runs. The initial field and pose use the same seed; the requested task changes the control decision.
3. Compare the first `action_delta_ne_m` in each `steps.jsonl`. Describe the movement with north, south, east and west.
4. Open `map_local.json`. Its coordinates are local NED metres. This file is not a GPS map or GeoJSON.
5. Notice that the replay includes an added crosshair, while saved model-input frames do not. Presentation overlays should not leak into model inputs.

## Troubleshooting

- `No module named litterlab`: confirm the terminal is in the kit root and the interpreter is the project `.venv`.
- `FileExistsError`: choose a fresh output folder rather than deleting a result you still need.
- A different can result: retain the command and environment record; inspect whether the seed, model or source changed.

## Completion check

Save the three trajectories, the test log and your environment record. Explain in five sentences why the initial scene stays fixed while the trajectories differ. You pass when you can locate an observation, action, accepted target and outcome in the files.

## Optional extension

Repeat only the can run with seed 8 in a new folder. Explain why this changes the scene as well as the resulting path. Do not describe either run as a real-drone experiment.

