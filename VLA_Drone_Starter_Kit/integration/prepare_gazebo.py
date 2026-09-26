"""Generate assets beside, never inside, a PX4 checkout. Runtime not verified.

The supplied default world preserves the checkout's physics and sensor systems.
Our model includes its existing x500; inspect the expanded SDF before flight.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def generate(px4, out):
    base = Path(px4) / "Tools/simulation/gz"
    world = ET.parse(base / "worlds/default.sdf")
    if not (base / "models/x500/model.sdf").is_file():
        raise FileNotFoundError("Initialise PX4 submodules and confirm the x500 model path")
    out = Path(out); out.mkdir(parents=True, exist_ok=False)
    (out / "worlds").mkdir(); model_dir = out / "models/x500_litter"; model_dir.mkdir(parents=True)
    w = world.getroot().find("world"); w.set("name", "litter")
    if not any(p.get("name") == "gz::sim::systems::Sensors" for p in w.findall("plugin")):
        plugin = ET.SubElement(w, "plugin", {"filename": "gz-sim-sensors-system", "name": "gz::sim::systems::Sensors"})
        ET.SubElement(plugin, "render_engine").text = "ogre2"
    truth = []
    for category, north, east, colour in [("bottle", 2., 1., "0.9 0.1 0.1 1"),
                                         ("can", -1., 2., "0.1 0.2 0.9 1"),
                                         ("paper", -2., -1., "0.95 0.85 0.1 1")]:
        # Gazebo ENU: x=east, y=north, z=up. These oversized targets teach geometry.
        m = ET.SubElement(w, "model", {"name": f"litter_{category}"})
        ET.SubElement(m, "static").text = "true"
        ET.SubElement(m, "pose").text = f"{east} {north} 0.025 0 0 0"
        link = ET.SubElement(m, "link", {"name": "body"})
        for kind in ["visual", "collision"]:
            element = ET.SubElement(link, kind, {"name": kind})
            box = ET.SubElement(ET.SubElement(element, "geometry"), "box")
            ET.SubElement(box, "size").text = "0.3 0.3 0.05"
            if kind == "visual":
                material = ET.SubElement(element, "material")
                ET.SubElement(material, "ambient").text = colour
                ET.SubElement(material, "diffuse").text = colour
        truth.append({"category": category, "north_m": north, "east_m": east})
    ET.indent(world, space="  "); world.write(out / "worlds/litter.sdf", encoding="unicode", xml_declaration=True)
    model = '''<?xml version="1.0"?>
<sdf version="1.9"><model name="x500_litter">
  <include merge="true"><uri>model://x500</uri></include>
  <link name="litter_camera_link">
    <pose>0 0 -0.12 0 0 0</pose>
    <inertial><mass>0.01</mass><inertia><ixx>0.00001</ixx><iyy>0.00001</iyy><izz>0.00001</izz></inertia></inertial>
    <sensor name="litter_camera" type="camera">
      <pose>0 0 0 0 1.57079632679 0</pose>
      <always_on>true</always_on><update_rate>10</update_rate>
      <topic>/litter_camera/image</topic>
      <camera><horizontal_fov>1.57079632679</horizontal_fov>
        <image><width>640</width><height>640</height><format>R8G8B8</format></image>
        <clip><near>0.05</near><far>100</far></clip>
      </camera>
    </sensor>
  </link>
  <joint name="litter_camera_joint" type="fixed"><parent>base_link</parent><child>litter_camera_link</child></joint>
</model></sdf>
'''
    (model_dir / "model.sdf").write_text(model)
    (model_dir / "model.config").write_text('<model><name>x500_litter</name><version>1.0</version><sdf version="1.9">model.sdf</sdf></model>')
    (out / "evaluator_only.json").write_text(json.dumps(truth, indent=2))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--px4", required=True); ap.add_argument("--out", required=True)
    args = ap.parse_args(); print(generate(args.px4, args.out))
