# Assumptions and limitations

## Included in the core model

- Spherical Earth with mean radius 6,378,000 m.
- Circular orbit and standard gravitational parameter `GM`.
- Weak-field gravitational time dilation.
- Stationary, non-rotating ground reference clock.
- First-order addition of the SR and GR clock-rate corrections.
- Constant clock-rate offsets when accumulating over the selected interval.

## Excluded effects

The model omits orbital eccentricity, Earth's rotation and geoid, Sagnac correction, signal propagation effects, atmospheric delays, multipath, satellite orbit errors, receiver clock bias, and other operational GPS corrections. Sagnac is a signal-propagation correction associated with Earth's rotating reference frame; it is separate from the gravitational clock-rate correction.

Operational GPS accounts for additional effects and pre-adjusts satellite clock frequencies. The `cΔt` value shown here is a pseudorange-equivalent clock error, not the receiver's actual position error. Receivers estimate their clock bias and position using signals from multiple satellites. This application is an educational model, not a complete operational GPS receiver.
