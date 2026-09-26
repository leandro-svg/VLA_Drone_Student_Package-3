# Lab 6 Establish a repeatable flight simulator

**Where:** Ubuntu 22.04 lab host. **Before starting:** Labs 1–5 and access to the host. **Theory:** guide pages 29 and 34. **Status:** supplied integration procedure; runtime validation pending.

## Goal

Run the real autopilot against a simulated vehicle and document an environment that can be restarted. Identify what PX4 controls, what Gazebo simulates and what the companion program requests.

## Mac preparation

Draw three boxes for PX4, Gazebo and the companion Python process. Add arrows for simulated sensors, actuator commands, telemetry and offboard setpoints. Read `integration/prepare_gazebo.py` and `docs/PX4.md`. This preparation is useful locally; completing it does not establish a working simulator.

The workbook route runs the simulator stack on one Ubuntu machine. Use your Mac for editing and remote desktop. Native macOS Gazebo Classic instructions do not establish compatibility with this Harmonic exercise. Keep an experimental VM or native port in a separate environment record.

## Predict before running

The CPU teaching simulator uses a kinematic point vehicle. Which new failure modes might appear with a real estimator and autopilot? Explain why passing geometry tests cannot validate sensor startup or vehicle stability.

## Set up on the Ubuntu host

Have the lab engineer review the dependency setup on the designated machine. The setup script changes system packages. In a new checkout directory:

```sh
git clone --recursive --branch v1.16.0 \
  https://github.com/PX4/PX4-Autopilot.git
cd PX4-Autopilot
bash Tools/setup/ubuntu.sh
```

Follow any reboot instructions. Then, from that checkout:

```sh
git rev-parse HEAD
git submodule status
cat /etc/os-release
gz sim --versions
make px4_sitl gz_x500
```

PX4 v1.16.0 and Gazebo Harmonic are candidate pins for this package. Record what actually installed; retain build errors rather than silently switching versions. Use the matching official Ubuntu setup documentation linked in the workbook index.

## Inspect and restart

1. Confirm the default world and x500 load. Save the simulator view and PX4 console log.
2. Check that simulated sensor messages and position readiness appear. Record any missing sensor or estimator warning.
3. Close the simulator cleanly. Start it again from a fresh terminal with the same command.
4. Record the OS, PX4 commit, submodules, Gazebo version and launch command in `notes/lab06.md` on the host. Retain a copy alongside the Mac notes.

## Troubleshooting

Build failure: inspect the first compiler or dependency error. Missing models: verify submodules and resource paths. Rendering failure: inspect the host's graphics setup and remote desktop support. Fix the default world before generating the custom one.

## Completion check

Pass only when the default simulator starts twice from recorded instructions and provides usable sensor/vehicle state. Save logs from both runs. If no Ubuntu host is available, record the lab as blocked by environment and continue Lab 11A locally.

