# Lab 7 Verify camera images and ground geometry

**Where:** Ubuntu simulator host; offline XML preparation on Mac. **Before starting:** Lab 6 default simulator. **Theory:** guide pages 30–31 and 40–42. **Status:** generated XML tested structurally; rendering and calibration pending.

## Goal

Generate the litter field, record images and measure the camera's coordinate convention. Establish what a timestamp means before using an image to command motion or locate an object.

## Predict before running

For a nadir camera over a flat surface, doubling altitude should approximately halve a marker's pixel width. Predict how a marker moves in the image when it moves north or east. Mark which predictions depend on yaw and camera mounting.

## Generate and launch

Close the default simulator. In the kit root on Ubuntu, activate its CPU environment. Set `LITTER_PX4` to the actual checkout path; the value below is an example. Derive the kit path from the current directory so spaces remain quoted.

```sh
export LITTER_KIT="$PWD"
export LITTER_PX4="$HOME/PX4-Autopilot"
python -m integration.prepare_gazebo \
  --px4 "$LITTER_PX4" --out runs/lab07-assets
export LITTER_ASSETS="$LITTER_KIT/runs/lab07-assets"
export LITTER_GZ="$LITTER_PX4/Tools/simulation/gz"
export GZ_SIM_RESOURCE_PATH="$LITTER_ASSETS/models:$LITTER_ASSETS/worlds"
export GZ_SIM_RESOURCE_PATH="$GZ_SIM_RESOURCE_PATH:$LITTER_GZ/models"
export GZ_SIM_RESOURCE_PATH="$GZ_SIM_RESOURCE_PATH:$LITTER_GZ/worlds"
cd "$LITTER_PX4"
PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500_litter \
  PX4_GZ_WORLD=litter ./build/px4_sitl_default/bin/px4
```

In a second Ubuntu terminal, enter the kit root again. Use the Python environment containing Gazebo Transport 13, Messages 10 and Pillow:

```sh
gz topic -l
gz topic -i -t /litter_camera/image
python3 -c "from gz.transport13 import Node; from gz.msgs10.image_pb2 import Image"
python3 -m integration.record_camera --out runs/lab07-camera --seconds 10
```

Follow `docs/PX4.md` and the Gazebo Python source link for binding installation. Installing Pillow in one environment does not install Gazebo bindings in it.

## Measure four properties

1. Confirm readable RGB 640×640 frames with visible targets. The sensor requests 10 Hz; measure achieved simulation-time intervals and count gaps rather than requiring exactly 100 received frames.
2. Check that `sim_time_s` increases. Keep host arrival time separate from simulation time.
3. At a verified stationary pose, move a labelled marker north then east. Repeat at a changed yaw. Save the images and record the camera-to-body axes.
4. Repeat at two known heights and compare marker widths. Include measurement uncertainty and actual dimensions.

Use the simulator controls or a lab-reviewed hover procedure for stationary measurements. The recorder itself does not hold the vehicle. Its images have no synchronized capture pose yet.

## Troubleshooting and completion

No images: inspect topic names, the Sensors plugin and render logs. Wrong axes: inspect the camera link, sensor pose and yaw convention. The toy north-up projection is insufficient when those assumptions change.

Pass with a labelled axis image, a height/scale comparison, timestamp statistics and a written transform convention. Mac-only XML inspection passes preparation only. Keep generated evaluator truth out of the policy loader.

