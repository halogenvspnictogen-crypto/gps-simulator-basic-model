# GPS Relativity Simulator

An interactive physics laboratory for exploring how special and general relativity change GPS satellite clock rates. Designed for first-year undergraduate engineering students, the app keeps the physics in a standalone Python package and uses Streamlit and Plotly for interactive exploration.

## What it simulates

- Circular orbital radius, speed, and period.
- Special-relativistic clock slowing from satellite motion.
- Weak-field gravitational clock speeding at satellite altitude.
- First-order combined clock-rate correction.
- Accumulated clock difference and its pseudorange-equivalent distance, `Δd = cΔt`.

The standard GPS reference gives approximately **−7.209 μs/day SR**, **+45.662 μs/day GR**, **+38.453 μs/day net**, and **+11.528 km/day range-equivalent drift**. The last quantity is not a prediction of final receiver position error: a real receiver estimates its clock bias and position from multiple satellite signals.

## Features

1. Overview with reference results and comparison chart.
2. SR lab with independent velocity what-if control and curve.
3. GR lab with altitude control and potential values.
4. Combined GPS clock correction with orbit calculations and reset.
5. Positioning error accumulator for 1 hour, 1 day, 7 days, or 30 days.
6. Experiment lab with altitude sweeps, reference comparison, and accumulated clock plot.
7. Theory & Derivations chapter with step-by-step orbital, SR, and GR derivations.
8. Theory & Assumptions guide for scope and omitted operational effects.

## Technology

Python, Streamlit, NumPy, and Plotly. Physics functions use SI units and can be imported without Streamlit. The SR expression uses a cancellation-safe algebraic identity for small speeds.

## Project structure

```text
GPS_RELATIVITY_SIMULATOR/
├── app.py
├── requirements.txt
├── README.md
├── physics/
├── tests/
└── docs/
```

## Install and run on Windows

Open PowerShell in the project directory:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Model assumptions and limitations

The model assumes a spherical Earth, circular orbit, standard gravitational parameter, weak-field gravitational time dilation, a stationary non-rotating surface reference clock, and first-order addition of SR and GR rate differences. It omits orbital eccentricity, Earth's rotation and geoid, Sagnac correction, signal propagation effects, atmospheric delays, multipath, satellite orbit errors, receiver clock bias, and other operational GPS corrections. Sagnac is a signal-propagation correction associated with Earth's rotating frame, not the gravitational clock-rate correction. Operational GPS accounts for additional effects and pre-adjusts satellite clock frequencies; this simulator is not a complete GPS receiver.

In the conventional pseudorange equation, positive receiver clock bias adds `+cδt_r` and positive satellite clock bias adds `−cδt_s`. The simulator's range plot instead shows signed `cΔt` for the satellite clock difference; the magnitude is the equivalent range offset, not final receiver position error.

See [docs/MATH_MODEL.md](docs/MATH_MODEL.md) for derivation and [docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md) for details.
