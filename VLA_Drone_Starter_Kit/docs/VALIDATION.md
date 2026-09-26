# Validation record

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
