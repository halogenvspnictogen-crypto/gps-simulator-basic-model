# Mathematical model and derivation

All calculations use SI units internally. Constants: `c = 299792458 m/s`, `GM = 3.986004418×10^14 m³/s²`, equatorial Earth radius `R_E = 6378000 m`, and standard GPS altitude `h = 20200000 m`. Orbital radius is measured from Earth's centre:

```text
r = R_E + h = 6378000 + 20200000 = 26578000 m
```

Altitude is the height above the reference surface; radius includes the Earth radius.

## Circular orbit

Newtonian gravitation provides the centripetal acceleration required for circular motion. Equate gravitational attraction to the centripetal-force requirement:

```text
GMm/r² = mv²/r
GM/r² = v²/r       (cancel m)
GM/r = v²
v = √(GM/r)
```

At the reference radius, `v = 3872.645 m/s`. One circular orbit has circumference `2πr`, so `T = 2πr/v = 43121.556 s ≈ 11.98 hours`. This assumes a central spherical Earth and a circular orbit.

## Special relativity

Proper time `Δτ` is measured by a clock along its own path. Coordinate time `Δt` here is the chosen stationary reference frame's time. In a light-clock thought experiment, mirrors are separated by `L`. At rest, light travels one half-cycle vertically: `cΔτ/2=L`. For an observer seeing the clock move at speed `v`, that light travels a diagonal path:

```text
(cΔt/2)² = L² + (vΔt/2)²
L = cΔτ/2
c²Δt² = c²Δτ² + v²Δt²
Δτ/Δt = √(1−v²/c²)
γ = 1/√(1−v²/c²)
```

Thus the satellite clock's fractional rate difference from a stationary clock is `ε_SR = √(1−v²/c²)−1`. It is negative because the moving clock rate ratio is less than one. For standard GPS, `ε_SR ≈ −8.3434194×10⁻¹¹` and `Δt_SR = ε_SR×86400 s = −7.208714 μs/day`.

For numerical stability, the implementation uses the algebraically equivalent form with `x=v²/c²`:

```text
ε_SR = −x/(1+√(1−x))
```

This avoids cancellation from subtracting two nearly equal numbers when `x` is very small.

## General relativity

With potential zero at infinity, Newtonian gravitational potential is `Φ=−GM/r`, negative near Earth and less negative at larger radius. For a stationary clock in the ideal Schwarzschild spacetime:

```text
dτ/dt = √(1−2GM/(rc²))
```

Since `2GM/(rc²)` is very small for Earth, use `√(1−x)≈1−x/2`:

```text
dτ/dt ≈ 1−GM/(rc²) = 1+Φ/c²
```

For stationary satellite-radius and surface clocks, respectively, the first-order relative rate is:

```text
dτ_S/dt ≈ 1+Φ_S/c²
dτ_E/dt ≈ 1+Φ_E/c²
dτ_S/dτ_E ≈ 1+(Φ_S−Φ_E)/c²
ε_GR = (Φ_S−Φ_E)/c² = GM/c²(1/R_E−1/r)
```

At positive altitude, `r>R_E`, making the result positive. Standard GPS gives `ε_GR ≈ +5.2849505×10⁻¹⁰` and `Δt_GR = ε_GR×86400 s = +45.661973 μs/day`.

The Schwarzschild stationary-clock expression is not the complete rate formula for the moving satellite. This educational model separates the leading kinematic SR contribution from the weak-field gravitational contribution, then combines them at first order.

## Combined correction and range equivalent

The first-order model is `ε_net≈ε_SR+ε_GR`; cross-products of corrections around `10⁻¹⁰` are around `10⁻²⁰` and neglected. The standard result is `ε_net≈+4.4506086×10⁻¹⁰`, or `+38.453258 μs/day`. GR dominates SR at this orbit, so the satellite clock gains time relative to the ground reference.

For elapsed duration `t`, clock difference is `Δt=εt`. The physics function `pseudorange_error(Δt)` returns the signed clock-derived range equivalent `cΔt`. At one day, this is `+11.527997 km/day` for the net rate. Its magnitude is about `11.528 km/day`.

In the conventional measurement equation `ρ=d+c(δt_r−δt_s)+I+T+ε`, a positive satellite clock bias contributes `−cδt_s`, while a positive receiver clock bias contributes `+cδt_r`. The simulator's signed `cΔt` convention tracks the satellite clock difference itself; it is not the conventional signed satellite-bias term. Range-equivalent magnitude is distinct from either signed quantity and is not final receiver position error.

## Numerical reference

| Quantity | Standard GPS value |
|---|---:|
| Orbital radius | 26,578,000 m |
| Orbital velocity | 3,872.645 m/s |
| Orbital period | 43,121.556 s ≈ 11.98 h |
| SR correction | −7.209 μs/day |
| GR correction | +45.662 μs/day |
| Net correction | +38.453 μs/day |
| Range-equivalent magnitude | ≈ 11.528 km/day |
