"""Special-relativistic rate of a moving clock relative to a stationary clock."""
import math
from .constants import C, DAY

def sr_fractional_rate(velocity_m_s: float) -> float:
    """Return sqrt(1-v²/c²)-1, evaluated with a cancellation-safe identity."""
    if not math.isfinite(velocity_m_s) or velocity_m_s < 0 or velocity_m_s >= C:
        raise ValueError("Velocity must be finite and satisfy 0 <= v < c.")
    x = (velocity_m_s / C) ** 2
    return -x / (1.0 + math.sqrt(1.0 - x))

def sr_daily_us(velocity_m_s: float) -> float:
    return sr_fractional_rate(velocity_m_s) * DAY * 1e6

def lorentz_factor(velocity_m_s: float) -> float:
    if not math.isfinite(velocity_m_s) or velocity_m_s < 0 or velocity_m_s >= C:
        raise ValueError("Velocity must be finite and satisfy 0 <= v < c.")
    return 1.0 / math.sqrt(1.0 - (velocity_m_s / C) ** 2)
