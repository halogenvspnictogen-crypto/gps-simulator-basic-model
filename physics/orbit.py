"""Circular-orbit calculations."""
import math
from .constants import EARTH_RADIUS, GM

def circular_orbit(altitude_m: float) -> dict[str, float]:
    """Return radius, speed, period and altitude for a circular orbit."""
    if not math.isfinite(altitude_m) or altitude_m < 0:
        raise ValueError("Altitude must be a finite, non-negative number of metres.")
    radius = EARTH_RADIUS + altitude_m
    velocity = math.sqrt(GM / radius)
    return {"altitude_m": altitude_m, "radius_m": radius, "velocity_m_s": velocity,
            "period_s": 2 * math.pi * radius / velocity}
