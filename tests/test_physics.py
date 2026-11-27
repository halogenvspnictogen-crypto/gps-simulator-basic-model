"""Independent numerical references and physical-invariant tests."""
import math
import unittest

from physics.constants import C, EARTH_RADIUS, GM, GPS_ALTITUDE, DAY
from physics.orbit import circular_orbit
from physics.special_relativity import sr_fractional_rate, sr_daily_us
from physics.general_relativity import gr_fractional_rate, gr_daily_us
from physics.clock_correction import gps_correction
from physics.navigation_error import pseudorange_error


class StandardReferenceTests(unittest.TestCase):
    def test_standard_gps_reference(self):
        result = gps_correction(GPS_ALTITUDE)
        self.assertAlmostEqual(result["radius_m"], 26_578_000, delta=0.01)
        self.assertAlmostEqual(result["velocity_m_s"], 3872.645, delta=0.002)
        self.assertAlmostEqual(result["sr_us_day"], -7.209, delta=0.001)
        self.assertAlmostEqual(result["gr_us_day"], 45.662, delta=0.002)
        self.assertAlmostEqual(result["net_us_day"], 38.453, delta=0.002)
        self.assertAlmostEqual(result["period_s"] / 3600, 11.98, delta=0.01)
        self.assertAlmostEqual(pseudorange_error(result["net_fractional"] * DAY) / 1000,
                               11.528, delta=0.002)

    def test_signs_and_net_sum(self):
        result = gps_correction(GPS_ALTITUDE)
        self.assertLess(result["sr_fractional"], 0)
        self.assertGreater(result["gr_fractional"], 0)
        self.assertGreater(result["net_fractional"], 0)
        self.assertEqual(result["net_fractional"], result["sr_fractional"] + result["gr_fractional"])


class InvariantTests(unittest.TestCase):
    def test_faster_motion_has_more_negative_sr(self):
        self.assertLess(sr_fractional_rate(5000), sr_fractional_rate(3000))

    def test_more_altitude_increases_gr_difference(self):
        self.assertGreater(gr_fractional_rate(20_200_000), gr_fractional_rate(10_000_000))

    def test_zero_velocity_is_zero_sr(self):
        self.assertEqual(sr_fractional_rate(0), 0.0)

    def test_zero_altitude_is_zero_differential_gr(self):
        self.assertEqual(gr_fractional_rate(0), 0.0)

    def test_small_speed_stable(self):
        speed = 1e-3
        expected = -(speed / C) ** 2 / (1 + math.sqrt(1 - (speed / C) ** 2))
        self.assertAlmostEqual(sr_fractional_rate(speed), expected, delta=1e-40)
        self.assertLess(sr_fractional_rate(speed), 0)

    def test_range_conversion_is_c_times_time(self):
        dt = 0.123456789
        self.assertEqual(pseudorange_error(dt), C * dt)

    def test_orbit_invariant(self):
        orbit = circular_orbit(GPS_ALTITUDE)
        self.assertAlmostEqual(GM / orbit["radius_m"]**2,
                               orbit["velocity_m_s"]**2 / orbit["radius_m"], places=15)


class InputValidationTests(unittest.TestCase):
    def test_negative_altitude_rejected(self):
        for fn in (circular_orbit, gr_fractional_rate):
            with self.assertRaises(ValueError): fn(-1)

    def test_invalid_altitudes_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError): circular_orbit(value)

    def test_invalid_velocities_rejected(self):
        for value in (-1, C, C + 1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError): sr_fractional_rate(value)


if __name__ == "__main__":
    unittest.main()
