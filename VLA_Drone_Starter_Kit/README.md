# VLA Drone Starter Kit

**Research target:** one VLA decides when to pause a survey, inspect and map litter, then resume. This kit supplies the foundational movement exercises; the complete mission model remains research implementation work. Read [docs/SINGLE_VLA.md](docs/SINGLE_VLA.md).


Use this code alongside the **[Complete Thesis Guide](../Guide/VLA_Drone_Complete_Thesis_Guide_VUB.pdf)**, which combines the research handbook, ten introductory labs and two research build labs. This is a teaching project and a set of lab integration exercises, not a flight-ready drone system.

## What runs now

The `litterlab` package runs on an ordinary laptop with Python 3.10 or newer, NumPy and Pillow. It implements a simple camera, a bounded position-command interface, expert demonstrations, a small imitation learner and closed-loop tests. Its objects are deliberately coloured circles. Its vehicle is a kinematic point mass. It does not simulate PX4, rotors, wind or realistic litter appearance.

From this directory on macOS or Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m litterlab demo --target can --out runs/first
python -m litterlab collect --out runs/data
python -m integration.data --data runs/data
python -m litterlab train --data runs/data --out runs/tiny
python -m litterlab evaluate --split val --out runs/classical-val
python -m litterlab evaluate --split val --model runs/tiny/policy.npz --out runs/learned-val
python -m litterlab evaluate --split val --model runs/tiny/policy.npz --language swapped --out runs/swapped-val
python -m litterlab evaluate --split val --model runs/tiny/policy.npz --language empty --out runs/empty-val
```

On Windows, activate with `.venv\Scripts\Activate.ps1` in PowerShell. Use a new output directory for every run; the commands deliberately refuse to overwrite an existing one.

Open `runs/first/replay.gif`, `trajectory.png`, `result.json`, `steps.jsonl` and `map_local.json`. Read the corresponding labs in the complete guide before modifying the model.

Evaluation defaults to `--split val` (seeds starting at 100000). Once the model and protocol are frozen, use `--split test` (seeds starting at 200000):

```sh
python -m litterlab evaluate --split test --out runs/classical-test
python -m litterlab evaluate --split test --model runs/tiny/policy.npz --out runs/learned-test
python -m litterlab evaluate --split test --model runs/tiny/policy.npz --language swapped --out runs/swapped-test
python -m litterlab evaluate --split test --model runs/tiny/policy.npz --language empty --out runs/empty-test
```

The PDF/Word guide's original evaluation commands used test scenes implicitly. Add `--split test` when reproducing its reported results; use validation scenes for development. Summaries now identify the split, and trial records include the actual input instruction. Swapped and empty instructions require `--model`; they remain scored against the original requested target.

## Files

- `litterlab/core.py`: rendering, coordinates, kinematic environment and classical controller.
- `litterlab/learning.py`: small NumPy MLP and supervised training. This is **not SmolVLA** and does not learn an image encoder or a language model.
- `litterlab/__main__.py`: command line, expert episodes and closed-loop evaluation.
- `integration/data.py`: dataset contract validator and observation/action-only reader.
- `integration/export_lerobot.py`: optional export to LeRobot v0.4.4, one split at a time, no upload.
- `integration/train_smolvla.py`: GPU adaptation exercise using the native flow-matching objective.
- `integration/evaluate_smolvla.py`: image-and-language closed-loop evaluation of the adapted model in the toy simulator.
- `integration/prepare_gazebo.py`: generate a world and nadir-camera model beside a PX4 checkout.
- `integration/record_camera.py`: capture Gazebo image messages with simulation timestamps.
- `integration/px4_square.py`: local SITL position-command exercise.
- `docs/SMOLVLA.md`, `docs/PX4.md`: integration commands and pass criteria.
- `docs/VALIDATION.md`: what was actually executed and what remains unverified.
- `../Guide/`: the complete 84-page illustrated guide in PDF and editable Word formats.
- `examples/`: one verified baseline episode, tiny-model checkpoint and measured evaluation summaries.

The test set is for final comparisons. Do not adjust the model after seeing its test result and present a rerun as an untouched test. Make further development changes against validation scenes, then reserve a new test set.

## Included teaching dataset

`examples/teaching_dataset/` contains the 210 simulated demonstration episodes used for the reported teaching experiment: 150 training, 30 validation and 30 test episodes. It includes images, action records, evaluator-only truth, a split manifest and compact feature arrays. It is synthetic teaching data, not an aerial field dataset.

Follow Lab 3 to generate your own copy in `runs/data`. To inspect the included copy first, run:

```sh
python -m integration.data --data examples/teaching_dataset
```

If you use the supplied data for training, pass `--data examples/teaching_dataset` instead of `--data runs/data`. Keep the supplied test split out of development. The saved checkpoint in `examples/tiny_model/` is the NumPy teaching learner, not SmolVLA.

Dataset validation requires `samples.npz` and checks its shapes, finite values, split membership, episode IDs, features and actions against the source images and records. The tiny trainer performs this validation before creating its output directory. If the cache is missing or stale, regenerate a complete dataset in a new directory using `litterlab collect`.

## Software and model downloads

Python dependencies, PX4/Gazebo, LeRobot and pretrained model weights are installed or downloaded using the documented commands; they are not included in this ZIP. The laptop exercises need only Python, NumPy and Pillow. Later GPU and simulator labs require the separate environments described in the guide and `docs/`.
