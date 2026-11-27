# Mathematical model

All internal values use SI units. The constants are `c = 299792458 m/s`, `GM = 3.986004418×10^14 m³/s²`, `R_E = 6378000 m`, and standard GPS altitude `h = 20200000 m`.

## Circular orbit

The orbital radius is `r = R_E + h`. Equating gravitational and centripetal force, `GMm/r² = mv²/r`, gives `v = √(GM/r)`. The period is `T = 2πr/v`. This assumes an ideal circular orbit around a spherical, non-rotating Earth.

## Special relativity

Relative to a stationary observer, the moving clock rate is `√(1−v²/c²)`. Its fractional difference is `ε_SR = √(1−v²/c²)−1`. With `x=v²/c²`, the implementation evaluates the equivalent `−x/(1+√(1−x))` to avoid subtracting nearly equal numbers. A negative daily correction means the moving satellite clock loses time.

## General relativity

In the weak-field approximation, `dτ/dt ≈ 1 + Φ/c²`, with Newtonian potential `Φ=−GM/r`. Relative to the surface clock, `ε_GR = GM/c²(1/R_E−1/r)`. At positive altitude this is positive: the satellite clock gains time.

## Combined rate and range equivalent

The educational first-order model adds the fractional corrections: `ε_net=ε_SR+ε_GR`. For elapsed duration `t`, each clock difference is `Δt=εt`. A clock offset maps to a pseudorange-equivalent distance `Δd=cΔt`. This distance is not a direct receiver position-error estimate because a navigation receiver solves for position and receiver clock bias from several satellite measurements.

## Numerical reference

| Quantity | Standard GPS value |
|---|---:|
| Orbital radius | 26,578,000 m |
| Orbital velocity | 3,872.645 m/s |
| Orbital period | about 11.98 h |
| SR correction | −7.209 μs/day |
| GR correction | +45.662 μs/day |
| Net correction | +38.453 μs/day |
| Pseudorange-equivalent drift | +11.528 km/day |
