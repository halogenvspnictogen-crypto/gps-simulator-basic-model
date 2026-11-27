"""Convert accumulated clock offsets to signal range-equivalent distances."""
from .constants import C

def pseudorange_error(clock_difference_s: float) -> float:
    """Return c*dt in metres; this is not a receiver position-error estimate."""
    return C * clock_difference_s
