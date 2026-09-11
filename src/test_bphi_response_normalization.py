"""Regression tests for the coefficient convention in disjoint bphi calibration."""
import unittest

import numpy as np

from fit_bphi_disjoint_response import conditional_bphi, fit_response


class ResponseNormalizationTest(unittest.TestCase):
    def setUp(self):
        self.b1 = 2.7317333004945543
        self.bphi = 4.2
        self.template_c = np.geomspace(6e-6, 5e-8, 14)
        rng = np.random.default_rng(31415)
        noise = rng.normal(size=(80, 14)) * self.template_c * 0.03
        self.noise = noise - noise.mean(axis=0)

    def test_known_bphi_recovered_without_double_division(self):
        response = self.b1 * self.bphi * self.template_c + self.noise
        result = fit_response(self.template_c, response)
        bphi, sigma = conditional_bphi(result["c_b1_times_bphi"], result["sigma_c_statistical"], self.b1)
        self.assertAlmostEqual(bphi, self.bphi, places=11)
        self.assertGreater(sigma, 0)
        self.assertLess(result["chi2"], 1e-18)

    def test_template_parameterizations_give_identical_prediction(self):
        response = self.b1 * self.bphi * self.template_c + self.noise
        response += (self.template_c * np.linspace(-.3, .3, 14))[None, :]
        per_c = fit_response(self.template_c, response)
        per_bphi = fit_response(self.b1 * self.template_c, response)
        bphi, sigma = conditional_bphi(per_c["c_b1_times_bphi"], per_c["sigma_c_statistical"], self.b1)
        self.assertAlmostEqual(bphi, per_bphi["c_b1_times_bphi"], places=11)
        self.assertAlmostEqual(sigma, per_bphi["sigma_c_statistical"], places=11)
        self.assertAlmostEqual(per_c["chi2"], per_bphi["chi2"], places=6)
        self.assertEqual(per_c["dof"], 13)
        self.assertGreater(per_c["sigma_c_hartlap"], per_c["sigma_c_statistical"])

    def test_invalid_inputs_fail(self):
        with self.assertRaises(ValueError):
            conditional_bphi(1, .1, 0)
        with self.assertRaises(ValueError):
            fit_response(np.zeros(14), self.noise)


if __name__ == "__main__":
    unittest.main()
