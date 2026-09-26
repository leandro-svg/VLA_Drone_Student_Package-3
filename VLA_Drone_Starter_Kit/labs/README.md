# VLA drone lab workbook

## How to use this workbook

This is the current practical route through all 12 labs. Start with the local exercises on your Mac, learn to interpret each result, then move to the simulator and model integration environments when they are available. The original 84-page thesis guide remains the theory and literature reference. This workbook supersedes its lab commands and completion checklists.

The aim is to explain and build the observation-to-action loop, then extend it to a complete survey mission. Running a command is only part of completing a lab. Before each experiment, write a prediction; afterwards, explain one observation and one limitation using saved evidence.

## Choose the environment

| Environment | Work | Current evidence |
| --- | --- | --- |
| Mac CPU | Labs 1–5, offline preparation for 6–10, Lab 11 logic, Lab 12 data tests | Laptop workflow executed on M4; research logic still to implement |
| Ubuntu 22.04 simulator host | Labs 6–8 and mission execution | PX4 v1.16.0 and Gazebo Harmonic are candidate pins; integration smoke tests pending |
| CUDA workstation | Labs 9–10 and larger Lab 12 training | Supplied scripts require CUDA; model runtime unverified |
| Apple GPU experiment | Optional future adaptation of 9–10 | MPS support must be implemented and measured; current scripts do not support it |
| Orin and aircraft | Deployment and real transfer after Lab 12 | Require separate equipment and experiments |

Your MacBook Air M4 with 24 GB unified memory is sufficient for the CPU route. The measured 33 GiB of free storage on 26 September 2026 is a snapshot; check again before simulator installations or model downloads. No VM, model download or hardware connection is needed for Labs 1–5.

Use an Ubuntu lab workstation through remote desktop for the simulator. Run Gazebo, PX4, camera recording and MAVSDK on that same Ubuntu host. Opening a terminal on your Mac does not move those processes onto the remote host. A VM or native macOS port is an optional compatibility project with separate evidence requirements.

## Learning order and prerequisites

Keep the original lab numbers so references in the thesis guide remain useful. The recommended order is **1–5, 11A, 6–8, 11B, 9–10, 12**. Lab 11A means the offline state-machine milestone; Lab 11B means integrating it with the validated simulator bridge.

| Lab | Subject | Needs | Evidence to save |
| --- | --- | --- | --- |
| [1](01_first_episode.md) | First episode | Mac setup | Three trajectories and environment record |
| [2](02_coordinates.md) | Coordinates and command anchoring | Lab 1 | Worked command and geometry checks |
| [3](03_dataset.md) | Demonstrations and information boundaries | Lab 2 | Validated dataset and one annotated sample |
| [4](04_training.md) | Train the tiny policy | Lab 3 | Checkpoint, loss history and selected epoch |
| [5](05_evaluation.md) | Evaluate and explain failures | Lab 4 | Paired validation results and failure replay |
| [6](06_simulator.md) | Default PX4 and Gazebo | Labs 1–5; Ubuntu | Restartable simulator and version record |
| [7](07_camera.md) | Camera and field geometry | Lab 6 | Images, timestamp checks and axis calibration |
| [8](08_commands.md) | Flight commands and bridge | Labs 6–7 | Square telemetry and separate bridge fault evidence |
| [9](09_smolvla_interface.md) | SmolVLA interface | Labs 3–5; CUDA for runtime | Tensor, gradient and reload checks |
| [10](10_smolvla_training.md) | SmolVLA development | Lab 9 | Checkpoint, validation behaviour and timing |
| [11](11_mission_manager.md) | Detour and resumption | Lab 5 for A; Lab 8 bridge for B | Event replay, recovery and coverage tests |
| [12](12_unified_vla.md) | Unified mission model | Labs 10 and 11B | Grouped missions and complete-system comparisons |

## Start the Mac environment

Open a terminal in `VLA_Drone_Starter_Kit`. Use your IDE's “Open in Integrated Terminal”, or type `cd ` and drag that folder into Terminal. This handles spaces in the folder name. Confirm that `ls` shows `litterlab`, `integration`, `tests` and `requirements.txt`.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m integration.lab_tools doctor
python -m unittest discover -s tests -v
```

Expect 22 passing tests in this revision. Our CPU verification used Python 3.14.6, NumPy 2.5.3 and Pillow 12.3.0. To reproduce those package versions with that Python version, use `requirements-cpu-tested.txt`. The broader `requirements.txt` is suitable for the supported CPU exercise environments; matching test results is the check, not merely completing installation.

Each new terminal needs `source .venv/bin/activate`. In VS Code, select `.venv/bin/python` as the interpreter. Keep the CUDA and simulator environments separate; this CPU environment does not install their dependencies.

## Evidence and run folders

All commands below run from the kit root unless explicitly stated. Use a fresh output folder per run. If one already exists, choose a new name and use it consistently in dependent commands. Existing run folders are deliberately protected from accidental overwrites.

```sh
mkdir -p notes
cp labs/WORKSHEET.md notes/lab01.md
python -m integration.lab_tools doctor > notes/environment.json
python -m pip freeze > notes/cpu-packages.txt
```

Copy the worksheet for each lab. Mark work as **not started**, **in progress**, **passed with evidence**, or **blocked by environment**. A local preparation exercise for a workstation lab does not earn its runtime pass.

## Corrections to the original guide

- The current suite has 22 tests; the original guide reports its historical ten-test run.
- Tiny-policy evaluation defaults to validation scenes. Use `--split val` for development and explicit `--split test` to reproduce the original 30/30 and 24/30 results.
- The dataset validator checks the cache against images and records. The trainer performs that check before training.
- Swapped and empty task interventions require a learned model; trials record the actual input instruction and retain the original requested goal for scoring.
- Labs 11 and 12 specify software to build. Their proposed filenames are not installed commands.
- Passing CPU tests does not validate PX4, Gazebo, SmolVLA, Orin or real flight.

## Reference sources

The external pages support platform setup and interfaces. The lab steps and assessment criteria are specific to this teaching package. Check the pinned versions before using examples from newer documentation.

- [PX4 v1.16 Ubuntu setup](https://docs.px4.io/v1.16/en/dev_setup/dev_env_linux_ubuntu)
- [PX4 v1.16 macOS setup](https://docs.px4.io/v1.16/en/dev_setup/dev_env_mac)
- [PX4 v1.16 Gazebo](https://docs.px4.io/v1.16/en/sim_gazebo_gz/)
- [Gazebo Transport 13 Python](https://gazebosim.org/api/transport/13/python.html)
- [LeRobot v0.4.4 source](https://github.com/huggingface/lerobot/tree/v0.4.4)
- [SmolVLA documentation](https://huggingface.co/docs/lerobot/smolvla)
- [Apple PyTorch and MPS](https://developer.apple.com/metal/pytorch/)

