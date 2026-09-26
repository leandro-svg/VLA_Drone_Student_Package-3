import unittest
import numpy as np
from litterlab.core import (bounded, pixel_to_offset, offset_to_pixel, Field,
                            classical, policy_features, detect_and_map)
from litterlab.__main__ import rollout


class Contracts(unittest.TestCase):
    def test_geometry_roundtrip(self):
        for ne in [[0,0],[1,2],[-2,1]]:
            np.testing.assert_allclose(pixel_to_offset(*offset_to_pixel(ne)),ne,atol=1e-12)

    def test_axis_signs(self):
        self.assertGreater(pixel_to_offset(48,30)[0],0)
        self.assertGreater(pixel_to_offset(60,48)[1],0)

    def test_invalid_actions(self):
        with self.assertRaises(ValueError):bounded([np.nan,0])
        with self.assertRaises(ValueError):bounded([0,0,0])
        self.assertAlmostEqual(np.linalg.norm(bounded([3,4])),.5)

    def test_anchor_not_repeated(self):
        field=Field(7); anchor=field.position.copy()
        accepted=field.apply([.5,0])
        np.testing.assert_allclose(accepted,anchor+[.5,0])
        self.assertLess(np.linalg.norm(field.position-anchor),.5)

    def test_observation_does_not_expose_truth(self):
        obs=Field(7).observe()
        self.assertFalse(hasattr(obs,"objects"))
        self.assertEqual(policy_features(obs,1).shape,(14,))

    def test_map_projection(self):
        field=Field(7); points=detect_and_map(field.observe())
        self.assertEqual(len(points),3)
        for prediction,(_,truth) in zip(points,field.objects):
            self.assertLess(np.linalg.norm(np.array(prediction["local_ned_m"][:2])-truth),.15)

    def test_classical_reaches_all_requested_categories(self):
        for target in range(3):
            self.assertTrue(rollout(7,target)[3])

    def test_absent_object_holds(self):
        np.testing.assert_allclose(classical(Field(7,missing=1).observe(),1),0)


if __name__=="__main__":unittest.main()
