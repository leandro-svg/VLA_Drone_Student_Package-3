# Lab 2 Trace coordinates and command anchoring

**Where:** Mac CPU. **Before starting:** Lab 1 can episode. **Theory:** guide pages 9–10, 19–20 and 23. **Status:** runnable teaching exercise.

## Goal

Distinguish pixels, relative displacement, absolute position targets and measured position. Explain why one prediction must be anchored once to the pose associated with its observation.

## Predict before running

For the ideal 96-pixel camera, the centre is `(48, 48)`, focal length is 48 pixels and height is 5 m. A target at `(60, 36)` lies north and east. Compute its ground offset and then scale the vector to a maximum length of 0.5 m. Does bounding each component separately give the same vector-length limit?

## Run the checks

```sh
python -m integration.lab_tools episode runs/lab01-can
python - <<'PY'
from litterlab.core import pixel_to_offset, bounded
offset = pixel_to_offset(60, 36)
print('Ground offset NE in metres:', offset)
print('Bounded command NE in metres:', bounded(offset))
PY
```

The worked offset is `[1.25, 1.25]` m. Its bounded command is approximately `[0.3536, 0.3536]` m. Both components can be below 0.5 while their combined vector exceeds 0.5, which is why the norm matters.

## Inspect one actual command

1. Take the first capture position and action from the Lab 1 can run. Add north to north and east to east by hand.
2. Compare with `accepted_position_ne_m`. The first seed-7 target is approximately `[-0.1204, -0.0103]` m.
3. Compare that target with the next row's measured position. The simulated vehicle needs time to approach a target; an accepted command is not proof that it has been reached.
4. Read `observe`, `classical`, `bounded` and `apply` in `litterlab/core.py`. Then read `rollout` in `litterlab/__main__.py`.
5. Explain why the logged down coordinate is `-5` for a vehicle 5 m above the local origin.

## Change one condition

In a scratch Python session, call `bounded([3, 4])`, then `bounded([float('nan'), 0])`. The first should have norm 0.5; the second should raise an error. Explain why silently passing NaN into a controller would make subsequent computations unreliable.

The geometry assumes a level nadir camera with north at image top. Write down which assumptions break when yaw, roll, pitch, terrain slope or camera mounting changes. Do not apply this projection unchanged to Gazebo imagery.

## Completion check

Save your hand calculation, helper output and axis sketch. Explain the capture anchor, vector bound, boundary clipping and measured response. Describe the error caused by adding the same displacement again on every command resend.

## Troubleshooting

If the helper reports that anchor plus action differs from the accepted target, inspect whether the simulator clipped the target at the field boundary. That can be valid behaviour. A sign mismatch at an interior point requires checking axis order and pixel direction.

