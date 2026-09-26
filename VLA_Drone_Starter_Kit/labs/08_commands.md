# Lab 8 Validate commands and build the observation bridge

**Where:** isolated Ubuntu SITL host; offline contract design on Mac. **Before starting:** Labs 6–7. **Theory:** guide pages 32–33. **Status:** square script supplied; synchronized bridge and independent supervisor remain implementation work.

## Goal

First demonstrate position tracking, then define and test the missing connection between camera observations and flight commands. Keep those two completion milestones explicit.

## Predict before running

If inference freezes but MAVSDK keeps resending the last setpoint, will PX4 necessarily detect an offboard stream failure? Explain why message streaming and fresh model decisions are different signals.

## Milestone A Run the square

Run the default or validated custom simulator on the same Ubuntu host as this script, with no physical aircraft connected. In a separate terminal at the kit root:

```sh
python3 -m venv .venv-flight
source .venv-flight/bin/activate
python -m pip install mavsdk==2.8.4
python -m integration.px4_square --sitl --out runs/lab08-square
```

The script connects to a local simulator, requests 5 m altitude, visits a 2 m square and lands. Each waypoint requires position error below 0.25 m and speed below 0.2 m/s for one second, with a 30-second timeout. These are exercise values.

Inspect `position.jsonl` and the PX4 flight log. Plot measured north/east against `target_ne`, identify each target change, and measure settling and overshoot. Speed is used by the script's reach check but is not saved in its current JSON log; use the PX4 log when analysing it. Do not treat host receive times as image capture times.

## Milestone B Implement the bridge

This is an assignment, not an existing command. Create a timestamped state buffer, observation matcher and separate command supervisor. Begin with recorded streams and a fake clock on your Mac, then connect them in SITL.

Each observation must identify its image, capture time, clock domain, interpolated estimated pose/attitude, calibration and task epoch. Each proposal must identify that observation, its capture anchor, action, computation time and expiry. Define and measure the clock mapping; reject out-of-buffer observations. Add the displacement to the capture anchor once, validate the absolute target, and resend that target while valid.

Agree timing tolerances and a hold response with the lab before executing bridge commands. The guide's 0.5 s validity and 20 Hz supervisor are initial hypotheses to test against measured delay and stopping behaviour.

## Fault cases and required evidence

| Injected fault | Required observation |
| --- | --- |
| Frozen image timestamp or stalled inference | Supervisor detects expiry and uses the reviewed response |
| NaN or out-of-bounds action | Proposal rejected with reason; no invalid target sent |
| Duplicate proposal | No repeated accumulation of displacement |
| Old task result after resumption | Task epoch rejection; new task retains authority |
| Missing pose near capture time | Observation rejected; no guessed pose association |
| Communication loss | Actual PX4 response matches reviewed offboard-loss configuration |

## Completion check

Milestone A passes with the square telemetry explained and landing confirmed. Milestone B passes with clock-alignment measurements, capture-anchor evidence and fault logs that include actual vehicle response. A Python `finally` block does not establish an independent watchdog. Policy-controlled SITL requires both milestones.

