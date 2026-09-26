# Lab 4 Train and inspect the tiny learner

**Where:** Mac CPU. **Before starting:** validated Lab 3 dataset. **Theory:** guide pages 25–26. **Status:** runnable teaching exercise.

## Goal

Understand how supervised action labels train a small model and how validation selects a checkpoint. Separate action agreement from successful behaviour.

## Predict before running

What should happen to training loss as the optimiser updates the model? Can lower action error guarantee that the vehicle reaches the right object? Write one reason a learned policy might enter states missing from expert demonstrations.

## Train and inspect

```sh
python -m litterlab train --data runs/lab03-data --out runs/lab04-tiny
python -m integration.lab_tools training runs/lab04-tiny
```

With defaults, training uses 200 epochs, batches of up to 128 samples, learning rate 0.002 and seed 0. The default dataset yields 1,800 optimiser updates. The original best validation normalised action MSE is approximately 0.0223172; exact equality across different environments is not a universal requirement.

## Read the model and its evidence

1. Read `TinyPolicy` in `litterlab/learning.py`: 14 inputs, two hidden layers of 64 units and two action outputs.
2. Count the 14 inputs: nine colour-centroid/presence features, three category indicators and two velocity values.
3. Read `config.json` and `history.json`. Identify the first, last and best validation epochs. The last epoch need not be the saved checkpoint.
4. Explain why labels are divided by 0.5 for training and predictions multiplied by 0.5 for execution. MSE in these normalised units is not an error in metres.
5. Explain what `policy.npz` stores. It is a NumPy checkpoint; it contains no pretrained vision or language backbone.

## A controlled comparison

Train a second run with `--epochs 20` and a fresh output directory. Hold the dataset and seed fixed. Compare the two loss histories using the helper. Write a prediction about their closed-loop performance before Lab 5 tests it. Do not select the better model from test scenes.

For plotting practice, plot `train_mse_normalised` and `val_mse_normalised` against `epoch` using a tool you already know. Keep the raw JSON next to the plot and label both axes and the chosen checkpoint.

## Completion check

Save the checkpoint, configuration, history and selected epoch. Explain episode, sample, batch, epoch, optimiser step and evaluation trial using this run's numbers. State which data changes the weights and which data selects the checkpoint.

## Troubleshooting

The trainer validates data before creating its output directory. Resolve cache or record inconsistencies first. For unexpected loss, check the dataset path, seed, action scale and package versions. More epochs will not repair an incorrect interface.

