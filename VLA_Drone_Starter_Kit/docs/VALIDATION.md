# Validation record

## Updated workbook verified on 26 September 2026

The current practical instructions are in `labs/README.md` and the twelve linked lab files. The original thesis guide remains a theory reference. New read-only helpers in `integration.lab_tools` report the environment, inspect an episode anchor, identify the selected tiny-model epoch and compare runs with matched starts.

- All 22 unit tests passed, including three additional teaching-helper tests.
- Executed the revised CPU route in temporary run folders on Python 3.14.6, NumPy 2.5.3 and Pillow 12.3.0.
- Lab 1 seed 7: can succeeded in 9 steps, bottle in 7 and paper in 6. Episode inspection confirmed the first capture anchor plus action matched the accepted target.
- Lab 3 regenerated 210 episodes and 1,569 samples, with no expert failures; the expanded validator passed.
- Lab 4 trained for 200 epochs / 1,800 updates. The helper identified epoch 119 as the selected checkpoint, with validation normalised action MSE 0.022317233243632904.
- Lab 5 validation scenes: classical 30/30, learned normal 29/30, swapped 0/30, empty 1/30. The normal-policy failure at seed 100000, bottle target, reproduced. The response-multiplier-2 extension achieved 27/30. These validation results are distinct from the historical test results below.
- CPU outputs used for this authoring check were temporary. These checks do not mark the student's worksheets complete.

The revised Labs 6–12 provide fuller prerequisites, procedures and acceptance criteria. Their simulator/GPU runtime and research implementation status is unchanged: no PX4/Gazebo launch, CUDA/MPS model run, mission-manager implementation, unified mission training or hardware operation was performed in this revision.

## Workflow fixes verified on 26 September 2026

Environment: Python 3.14.6, NumPy 2.5.3, Pillow 12.3.0, in an isolated temporary virtual environment.

- All 19 unit tests passed, including nine added workflow regression tests.
- Evaluation now defaults to validation scenes; `--split test` explicitly selects the original held-out scenes. Summaries record the split and trials record the actual input task.
- Classical swapped/empty language interventions are rejected before output creation. Learned interventions retain the original evaluation goal and log the changed input instruction.
- Dataset validation checks `samples.npz` against public images and records, including features, actions, shapes, finite values, episode IDs and splits. The tiny trainer validates before creating its output directory. Contract checks remain active with `python -O`.
- The bundled dataset passed the expanded validator: 1,144 train, 210 validation and 215 test samples.
- Explicit test-split evaluations reproduced all original summary values: classical 30/30, learned normal 24/30, swapped 0/30 and empty 0/30.
- A full 200-epoch retraining run produced weights identical to the bundled checkpoint, with 1,800 optimiser steps and best validation normalised action MSE 0.022317233243632904.
- All starter-kit Python sources parsed successfully. Run outputs were written to temporary directories; bundled examples were preserved.

This earlier revision increased the suite to 19 tests. The current workbook revision above brings it to 22. Follow the workbook for current commands; the original thesis guide reports the historical ten-test run. The optional GPU, simulator and hardware integrations remain unexecuted.

## Original teaching run

Executed on 26 September 2026. Environment: {'python': '3.12.14', 'numpy': '2.3.5', 'pillow': '12.3.0'}.

- 10 unit tests passed: frame signs, projection round trip, invalid commands, capture-anchor semantics, observation/ground-truth separation, mapping, absent-object hold for the classical policy, target-dependent classical navigation, asset XML structure, physical scaling.
- Baseline demo, seed 7, can target: success in 9 steps / 4.5 simulated seconds.
- Expert collection: 150 train / 30 validation / 30 test episodes, no expert failures, 1,569 samples (1,144 / 210 / 215).
- Dataset validator passed: grouped seeds, finite shapes and values, bounded labels, RGB files and 0.5-second timestamp increments.
- Tiny policy: 200 epochs, seed 0, 1,800 optimiser steps, best validation normalised action MSE 0.0223172. Checkpoint chosen using validation only.
- Held-out 30-scene evaluation: classical 30/30; learned normal instruction 24/30; learned swapped instruction 0/30 against the original requested goal; learned empty instruction 0/30.
- All Python sources passed syntax compilation.

These are teaching-simulator results. Swapped instructions deliberately change the target delivered to the policy while the evaluator retains the original target. This measures sensitivity to the task input; it is not evidence of general natural-language reasoning. The learner receives colour-centroid features and a category one-hot vector, not raw language embeddings. The test set was not used to tune the reported model after these results.

Not executed: LeRobot export, SmolVLA training/inference, pretrained-weight loading, PX4/Gazebo launch, simulator camera recording, MAVSDK flight, Orin runtime, hardware or outdoor experiments. Those dependencies/devices are unavailable in this authoring environment. Their scripts are concrete starting points and require the documented smoke tests. The paired real/simulation experiment is a proposed protocol, not a result.

The PNG/GIF and model files in `examples/` are actual outputs. The complete 210-episode teaching dataset is bundled in examples/teaching_dataset/ and can also be regenerated using the README commands. No training data or model is uploaded by these scripts.

## Single VLA mission edition

The updated guide specifies one shared model for mission events, grounding, semantics and inspection actions. Its mission heads, joint training, full mission manager and closed-loop survey are not implemented or executed by this starter kit. Labs 11 and 12 are research build exercises. The JSON records in templates/single_vla are illustrative schema examples; they are not recorded demonstrations. Existing teaching results above are unchanged.
