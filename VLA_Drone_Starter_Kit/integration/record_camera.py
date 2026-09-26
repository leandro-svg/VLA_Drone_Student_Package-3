"""Gazebo Harmonic camera recorder; runtime not verified here.

Run with Ubuntu's system Python after installing the matching Gazebo Python
bindings and Pillow. This logs simulator timestamps, not synchronised poses.
"""
import argparse
import json
from pathlib import Path
import threading
import time


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True)
    ap.add_argument("--seconds", type=float, default=10.)
    args = ap.parse_args()
    from gz.transport13 import Node
    from gz.msgs10.image_pb2 import Image as ImageMessage
    from PIL import Image
    out = Path(args.out); out.mkdir(parents=True, exist_ok=False)
    lock = threading.Lock(); count = 0
    def callback(message):
        nonlocal count
        with lock:
            w, h = message.width, message.height
            if message.step != w * 3 or len(message.data) != w * h * 3:
                raise ValueError("Recorder expects tightly packed R8G8B8 images")
            name = f"{count:06d}.png"
            Image.frombytes("RGB", (w, h), bytes(message.data)).save(out / name)
            row = {"frame": name, "sim_time_s": message.header.stamp.sec + message.header.stamp.nsec * 1e-9,
                   "host_arrival_monotonic_s": time.monotonic()}
            with (out / "frames.jsonl").open("a") as file: file.write(json.dumps(row) + "\n")
            count += 1
    node = Node()
    if not node.subscribe(ImageMessage, "/litter_camera/image", callback):
        raise RuntimeError("Could not subscribe to /litter_camera/image")
    time.sleep(args.seconds)
    if count == 0: raise RuntimeError("No frames: check gz topic -l and the Sensors world plugin")
    print(f"Recorded {count} frames; pose synchronisation is the next lab gate.")


if __name__ == "__main__": main()
