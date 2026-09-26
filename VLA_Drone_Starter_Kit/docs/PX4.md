# PX4 and Gazebo lab

**Status: source-reviewed integration exercises, not executed in PX4/Gazebo here.** Asset generation has a structural unit test, which does not validate Gazebo loading, camera orientation or flight. Work on an isolated software simulator with no physical aircraft connected.

Use the lab's Ubuntu 22.04 workstation, PX4 v1.16.0 and Gazebo Harmonic. Treat these as candidate pins to verify together. Start with the [PX4 Ubuntu setup](https://docs.px4.io/v1.16/en/dev_setup/dev_env_linux_ubuntu); the lab should perform the dependency installation and retain its environment record.

In a separate lab directory:

```sh
git clone --recursive --branch v1.16.0 https://github.com/PX4/PX4-Autopilot.git
cd PX4-Autopilot
bash Tools/setup/ubuntu.sh
make px4_sitl gz_x500
```

The setup script changes the workstation and may request administrator rights. Read its output and reboot if it requests it. First confirm the default simulator works. Close it before launching the custom world. Keep the PX4 console and simulator log.

Return to the starter-kit root. Set these two variables to your actual directories; the paths below are examples:

```sh
export LITTER_KIT="$HOME/VLA_Drone_Starter_Kit"
export LITTER_PX4="$HOME/PX4-Autopilot"
python -m integration.prepare_gazebo --px4 "$LITTER_PX4" --out runs/gazebo
export GZ_SIM_RESOURCE_PATH="$LITTER_KIT/runs/gazebo/models:$LITTER_KIT/runs/gazebo/worlds:$LITTER_PX4/Tools/simulation/gz/models:$LITTER_PX4/Tools/simulation/gz/worlds:${GZ_SIM_RESOURCE_PATH:-}"
cd "$LITTER_PX4"
PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_litter PX4_GZ_WORLD=litter ./build/px4_sitl_default/bin/px4
```

The generator copies the checkout's default world and adds three static, oversized coloured targets. Its model includes x500 and adds a nadir camera. It does not edit the checkout. It uses ENU for Gazebo object positions and records truth separately; do not feed that truth to the learned policy.

In a second terminal, with the same resource path:

```sh
gz topic -l
gz topic -i -t /litter_camera/image
```

Install the Harmonic Python transport/messages packages according to the [Gazebo Python documentation](https://gazebosim.org/api/transport/13/python.html). Use system Python with Pillow for the recorder if those bindings are outside your virtual environment:

```sh
cd "$LITTER_KIT"
python3 -m integration.record_camera --out runs/camera --seconds 10
```

Expect RGB 640×640 images and increasing simulation timestamps. No camera messages: inspect the world Sensors plugin and render errors. Do not continue with blank images. In hover, move a labelled marker north, then east; verify its image direction and the camera-to-body transform. Do not assume the toy north-up image convention holds at every yaw.

For the square exercise, use the separate flight-interface virtual environment:

```sh
python -m pip install mavsdk==2.8.4
python -m integration.px4_square --sitl --out runs/square
```

This script binds the local simulator port, arms the simulated vehicle, sets position targets at 5 m above local origin, traces a 2 m square, logs telemetry and lands. A point requires error below 0.25 m and speed below 0.2 m/s for one second, with a 30-second timeout. Record the PX4 log too. These thresholds are lab exercise values, not approved outdoor limits. Existing autopilot control remains unchanged.

## The integration gate that is still required

Camera recording and telemetry logging are separate demonstrations. **They are not yet a synchronized closed-loop VLA bridge.** Before policy control, the student and lab engineer must add timestamp-aligned observations, measured camera extrinsics, capture-anchored setpoints, a separate watchdog, and fault-injection tests. The complete guide specifies the bridge fields, matching rule and acceptance tests on page 33. The square script's host receive times are insufficient for moving-image geolocation; use the PX4 time-synchronisation facilities in the chosen bridge, or initially use stationary captures with verified timing. This gate needs supervision; it must not be skipped because the toy exercises pass.

[PX4 Gazebo configuration](https://docs.px4.io/v1.16/en/sim_gazebo_gz/) documents resource paths and model/world selection. [MAVSDK release](https://pypi.org/project/mavsdk/2.8.4/) is pinned to avoid mixing current examples with older imports.
