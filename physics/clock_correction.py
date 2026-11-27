"""Combine SR and GR contributions for the educational clock model."""
from .orbit import circular_orbit
from .special_relativity import sr_fractional_rate
from .general_relativity import gr_fractional_rate
from .constants import DAY

def gps_correction(altitude_m: float, velocity_m_s: float | None = None) -> dict[str, float]:
    orbit = circular_orbit(altitude_m)
    velocity = orbit["velocity_m_s"] if velocity_m_s is None else velocity_m_s
    sr = sr_fractional_rate(velocity)
    gr = gr_fractional_rate(altitude_m)
    net = sr + gr
    return {**orbit, "velocity_used_m_s": velocity, "sr_fractional": sr,
            "gr_fractional": gr, "net_fractional": net,
            "sr_us_day": sr * DAY * 1e6, "gr_us_day": gr * DAY * 1e6,
            "net_us_day": net * DAY * 1e6}
