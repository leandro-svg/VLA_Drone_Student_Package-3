import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from integration.prepare_gazebo import generate
from integration.data import STATE_SCALE, ACTION_SCALE


class ContractTests(unittest.TestCase):
    def test_gazebo_generator_preserves_world_and_adds_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); base = root / "px4/Tools/simulation/gz"
            (base / "worlds").mkdir(parents=True); (base / "models/x500").mkdir(parents=True)
            (base / "worlds/default.sdf").write_text('<sdf version="1.9"><world name="default"><gravity>0 0 -9.8</gravity></world></sdf>')
            (base / "models/x500/model.sdf").write_text('<sdf version="1.9"><model name="x500"/></sdf>')
            out = generate(root / "px4", root / "assets")
            world = ET.parse(out / "worlds/litter.sdf").getroot().find("world")
            self.assertEqual(world.find("gravity").text, "0 0 -9.8")
            self.assertEqual(len(world.findall("model")), 3)
            model = ET.parse(out / "models/x500_litter/model.sdf").getroot().find("model")
            self.assertEqual(model.find("link/sensor/topic").text, "/litter_camera/image")
            self.assertEqual(ET.parse(base / "worlds/default.sdf").getroot().find("world").get("name"), "default")

    def test_physical_scaling_round_trip(self):
        state = np.array([.2, -.3, 5., .1, -.1, 0., 1.])
        np.testing.assert_allclose(state / STATE_SCALE * STATE_SCALE, state)
        action = np.array([.3, -.4]); np.testing.assert_allclose(action / ACTION_SCALE * ACTION_SCALE, action)


if __name__ == "__main__": unittest.main()
