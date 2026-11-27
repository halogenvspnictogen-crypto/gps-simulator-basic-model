"""Weak-field gravitational clock-rate difference from Earth's surface."""
import math
from .constants import C, GM, EARTH_RADIUS, DAY

def gr_fractional_rate(altitude_m: float) -> float:
    if not math.isfinite(altitude_m) or altitude_m < 0:
        raise ValueError("Altitude must be a finite, non-negative number of metres.")
    radius = EARTH_RADIUS + altitude_m
    return GM / C**2 * (1.0 / EARTH_RADIUS - 1.0 / radius)

def gravitational_potential(radius_m: float) -> float:
    if not math.isfinite(radius_m) or radius_m <= 0:
        raise ValueError("Radius must be finite and greater than zero.")
    return -GM / radius_m

def gr_daily_us(altitude_m: float) -> float:
    return gr_fractional_rate(altitude_m) * DAY * 1e6
