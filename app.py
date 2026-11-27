"""GPS Relativity Simulator — interactive Streamlit teaching laboratory."""
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from physics.constants import C, GM, EARTH_RADIUS, GPS_ALTITUDE, DAY
from physics.orbit import circular_orbit
from physics.special_relativity import sr_fractional_rate, sr_daily_us, lorentz_factor
from physics.general_relativity import gr_fractional_rate, gr_daily_us, gravitational_potential
from physics.clock_correction import gps_correction
from physics.navigation_error import pseudorange_error

st.set_page_config(page_title="GPS Relativity Simulator", page_icon="🛰️", layout="wide")
st.markdown("""<style>
.stApp {background:radial-gradient(ellipse at 20% 0%,#14253a 0,#09111d 48%,#070c14 100%);color:#e7eef7}
[data-testid="stSidebar"]{background:#0b1522;border-right:1px solid #26384d}
.hero{padding:1.5rem 1.8rem;border:1px solid #29415a;border-radius:18px;background:linear-gradient(120deg,#14283c,#101b2a);margin-bottom:1rem}
.eyebrow{letter-spacing:.16em;text-transform:uppercase;color:#7ed9d0;font-size:.78rem;font-weight:700}
.metric{border:1px solid #263b50;border-radius:14px;padding:1rem;background:rgba(15,28,43,.82)}
.metric-label{color:#9db0c4;font-size:.85rem}.metric-value{font-size:1.65rem;font-weight:700;color:#f3f7fc;margin-top:.2rem}.metric-note{color:#6dd1c7;font-size:.82rem}
.callout{padding:1rem 1.2rem;background:#12283a;border-left:4px solid #58c8bb;border-radius:8px;margin:.7rem 0}
div[data-testid="stMetric"]{background:#101d2b;border:1px solid #263b50;padding:14px;border-radius:12px}
[data-testid="stMetricValue"]{color:#f3f7fc}
h1,h2,h3{color:#f3f7fc} p,li{color:#d2dce8}
</style>""", unsafe_allow_html=True)

PAGES = ["Overview", "Special Relativity Lab", "General Relativity Lab", "Combined GPS Correction", "Positioning Error", "Analysis / Experiment Lab", "Theory & Derivations", "Theory & Assumptions"]
with st.sidebar:
    st.markdown("## 🛰️ GPS Relativity")
    page = st.radio("Laboratory", PAGES, label_visibility="collapsed")
    st.divider()
    st.caption("REFERENCE ORBIT")
    st.metric("Altitude", "20,200 km")
    st.caption("Spherical Earth · circular orbit · first-order clock-rate model")

def chart_layout(fig, ytitle, title=None, xtitle=None):
    fig.update_layout(template="plotly_dark", title=title, height=390, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(9,17,29,.6)",
                      margin=dict(l=20,r=20,t=55,b=45), xaxis_title=xtitle, yaxis_title=ytitle,
                      font=dict(color="#d8e3ef"), legend=dict(orientation="h", y=1.12))
    fig.update_xaxes(gridcolor="#26384c", zerolinecolor="#8aa0b8")
    fig.update_yaxes(gridcolor="#26384c", zerolinecolor="#dce7f5", zerolinewidth=2)
    return fig

def correction_chart(c):
    fig=go.Figure()
    keys=[("Special Relativity","sr_us_day","#63a8ff"),("General Relativity","gr_us_day","#58d1bd"),("Net","net_us_day","#f7bd63")]
    values=[c[key] for _,key,_ in keys]
    low=min(0.0,min(values)); high=max(0.0,max(values))
    pad=max(1.0,(high-low)*0.06)
    for name,key,color in keys:
        fig.add_bar(name=name,x=[name],y=[c[key]],marker_color=color,text=[f"{c[key]:+.3f}"],textposition="outside")
    fig.update_layout(barmode="group",showlegend=False,yaxis=dict(range=[low-pad,high+pad]))
    return chart_layout(fig,"Clock correction (μs/day)","Daily clock-rate correction by component","Component")

def title(kicker,title,sub):
    st.markdown(f'<div class="hero"><div class="eyebrow">{kicker}</div><h1>{title}</h1><p>{sub}</p></div>',unsafe_allow_html=True)

def altitude_control(key="altitude_km", label="Satellite altitude", default=20200, maximum=40000):
    km=st.slider(label, min_value=0, max_value=maximum, value=int(st.session_state.get(key,default)), step=100, key=key, format="%d km")
    return km*1000.0

def metric_row(items):
    cols=st.columns(len(items))
    for col,(label,value,helptext) in zip(cols,items):
        col.metric(label,value,help=helptext)

standard=gps_correction(GPS_ALTITUDE)

if page=="Overview":
    title("PHYSICS LAB · GPS CLOCKS","GPS Relativity Simulator","Two small changes in clock rate decide whether satellite ranging stays accurate.")
    st.markdown("### Why relativity matters")
    st.write("GPS estimates distance from signal travel time. A satellite clock is moving rapidly, which makes it tick slower by special relativity, while its weaker gravitational field makes it tick faster by general relativity. At GPS altitude the gravitational contribution wins.")
    metric_row([("SR · slower",f'{standard["sr_us_day"]:+.3f} μs/day',"Satellite motion slows its clock."),("GR · faster",f'{standard["gr_us_day"]:+.3f} μs/day',"Higher altitude speeds its clock."),("NET · gain",f'{standard["net_us_day"]:+.3f} μs/day',"First-order sum of SR and GR."),("Range equivalent",f'{pseudorange_error(standard["net_fractional"]*DAY)/1000:+.3f} km/day',"Equivalent pseudorange offset, not final position error.")])
    st.plotly_chart(correction_chart(standard),width="stretch")
    st.markdown('<div class="callout"><b>Interpretation:</b> Ignoring the net clock difference would correspond to about 11.5 km of range-equivalent drift per day. A receiver estimates its own clock bias and position from multiple satellite signals, so this is not a direct prediction of receiver position error.</div>',unsafe_allow_html=True)
    st.markdown("#### Explore the laboratory")
    st.write("Use the navigation menu to isolate each effect, combine them for a circular GPS orbit, accumulate clock drift, or explore altitude-dependent trends. Controls update the calculations and graphs live.")
    with st.expander("Model at a glance"):
        st.latex(r"v=\sqrt{GM/r},\quad \epsilon_{SR}=\sqrt{1-v^2/c^2}-1,\quad \epsilon_{GR}=\frac{GM}{c^2}(1/R_E-1/r),\quad \epsilon_{net}=\epsilon_{SR}+\epsilon_{GR}")
        st.write("The model assumes a spherical Earth, circular orbit, and a stationary non-rotating surface reference clock.")

elif page=="Special Relativity Lab":
    title("ISOLATED EFFECT · MOTION","Special Relativity Lab","Change speed independently to see how motion alters a clock rate.")
    st.latex(r"\epsilon_{SR}=\sqrt{1-v^2/c^2}-1=-\frac{x}{1+\sqrt{1-x}},\quad x=v^2/c^2")
    st.write("A moving clock accumulates less proper time than the stationary reference clock. The negative sign means the satellite clock loses time in this comparison. This is an independent what-if experiment; the selected speed need not correspond to a circular GPS orbit.")
    gps_speed_km_s=standard["velocity_m_s"]/1000
    if "sr_velocity" not in st.session_state:
        st.session_state["sr_velocity"]=gps_speed_km_s
    if st.button("↺ Restore standard GPS orbit speed",key="sr_reset"):
        st.session_state["sr_velocity"]=gps_speed_km_s
    velocity=st.slider("Satellite speed (km/s)",0.0,30.0,step=0.01,format="%.3f",key="sr_velocity")*1000
    frac=sr_fractional_rate(velocity); rate=sr_daily_us(velocity)
    metric_row([("Speed",f"{velocity:,.3f} m/s","Input speed"),("Lorentz factor γ",f"{lorentz_factor(velocity):.12f}","γ = 1/√(1−v²/c²); dimensionless"),("Fractional rate",f"{frac:.6e}","Moving clock rate minus reference rate; dimensionless"),("Daily difference",f"{rate:+.4f} μs/day","Negative means the moving clock loses time")])
    speeds=np.linspace(0,30_000,301); vals=np.array([sr_daily_us(float(v)) for v in speeds])
    fig=go.Figure(go.Scatter(x=speeds/1000,y=vals,mode="lines",line=dict(color="#63a8ff",width=3),name="SR correction"));fig.add_vline(x=velocity/1000,line_dash="dash",line_color="#f7bd63")
    st.plotly_chart(chart_layout(fig,"SR correction (μs/day)","Motion makes the clock run slower","Satellite speed (km/s)"),width="stretch")

elif page=="General Relativity Lab":
    title("ISOLATED EFFECT · GRAVITY","General Relativity Lab","Compare weak-field clock rates at Earth's surface and above it.")
    st.latex(r"\Phi=-GM/r,\quad d\tau/dt\approx1+\Phi/c^2,\quad \epsilon_{GR}=\frac{GM}{c^2}(1/R_E-1/r)")
    st.write("The gravitational potential becomes less negative with altitude. A clock higher in the gravitational field accumulates more time relative to the surface clock, so this differential correction is positive.")
    altitude=altitude_control("gr_altitude_km")
    radius=EARTH_RADIUS+altitude; frac=gr_fractional_rate(altitude); rate=gr_daily_us(altitude)
    metric_row([("Altitude",f"{altitude/1000:,.0f} km","Above the reference surface"),("Surface potential",f"{gravitational_potential(EARTH_RADIUS):.4e} J/kg","Φ = −GM/Rₑ"),("Satellite potential",f"{gravitational_potential(radius):.4e} J/kg","Φ = −GM/r"),("Daily difference",f"{rate:+.4f} μs/day","Positive means higher clock gains time")])
    hs=np.linspace(0,40_000_000,301); ys=np.array([gr_daily_us(float(h)) for h in hs])
    fig=go.Figure(go.Scatter(x=hs/1000,y=ys,mode="lines",line=dict(color="#58d1bd",width=3),name="GR correction"));fig.add_vline(x=altitude/1000,line_dash="dash",line_color="#f7bd63")
    st.plotly_chart(chart_layout(fig,"GR correction (μs/day)","Higher altitude means a faster clock","Altitude above Earth's surface (km)"),width="stretch")
    st.caption("The horizontal axis is altitude above the spherical surface; the comparison is differential, so it is zero at zero altitude.")

elif page=="Combined GPS Correction":
    title("CENTRAL RESULT · CIRCULAR ORBIT","Combined GPS Clock Correction","The orbit model supplies velocity; both clock effects are then added at first order.")
    if st.button("↺ Restore standard GPS orbit",key="combined_reset"):
        st.session_state["combined_altitude_km"]=20200
    altitude=altitude_control("combined_altitude_km")
    c=gps_correction(altitude)
    metric_row([("Orbital radius",f'{c["radius_m"]/1000:,.0f} km',"Rₑ + altitude"),("Circular speed",f'{c["velocity_m_s"]:,.3f} m/s',"v = √(GM/r)"),("Orbital period",f'{c["period_s"]/3600:.3f} h',"T = 2πr/v"),("Net rate",f'{c["net_us_day"]:+.3f} μs/day',"Satellite clock gains for the standard GPS orbit")])
    st.plotly_chart(correction_chart(c),width="stretch")
    left,right=st.columns(2)
    with left:
        st.markdown("#### Special Relativity")
        st.latex(r"\epsilon_{SR}=\sqrt{1-v^2/c^2}-1")
        st.metric("Satellite loses",f'{c["sr_us_day"]:+.3f} μs/day')
    with right:
        st.markdown("#### General Relativity")
        st.latex(r"\epsilon_{GR}=\frac{GM}{c^2}(1/R_E-1/r)")
        st.metric("Satellite gains",f'{c["gr_us_day"]:+.3f} μs/day')
    st.markdown('<div class="callout"><b>Net interpretation:</b> SR makes the satellite clock lose time. GR makes it gain time. For standard GPS, GR is larger, so the net clock rate is faster than the surface reference clock.</div>',unsafe_allow_html=True)
    with st.expander("Numerical substitution and assumptions"):
        st.write(f"r = Rₑ + h = {EARTH_RADIUS:,.0f} m + {altitude:,.0f} m = {c['radius_m']:,.0f} m; v = √(GM/r) = {c['velocity_m_s']:,.3f} m/s.")
        st.write(f"ε_net = ε_SR + ε_GR = {c['sr_fractional']:.6e} + {c['gr_fractional']:.6e} = {c['net_fractional']:.6e}. The orbit is idealized as circular.")

elif page=="Positioning Error":
    title("ACCUMULATION · RANGE EQUIVALENT","Positioning Error Simulator","Translate accumulated clock differences into an equivalent signal range offset.")
    st.warning("The calculated range equivalent is not a direct estimate of actual receiver position error. It is the signal-distance equivalent of an uncorrected satellite clock offset, and this application does not implement a receiver or trilateration solver.")
    st.latex(r"\Delta d=c\,\Delta t")
    st.write("The controls below accumulate the SR, GR, and net clock-rate differences at the standard GPS orbit for the selected duration, and convert each accumulated clock difference into a signed range equivalent, cΔt.")
    c=gps_correction(GPS_ALTITUDE); hours=st.select_slider("Elapsed time",options=[1,24,24*7,24*30],value=24,format_func=lambda h:{1:"1 hour",24:"1 day",168:"7 days",720:"30 days"}[h],key="duration_hours")
    seconds=hours*3600; labels=["Special Relativity","General Relativity","Net"]
    components=[c["sr_fractional"]*seconds,c["gr_fractional"]*seconds,c["net_fractional"]*seconds]
    distances=[pseudorange_error(x) for x in components]
    metric_row([("Elapsed",f"{hours:g} h","Accumulation period"),("SR clock difference",f"{components[0]*1e6:+.3f} μs",f"Range equivalent {distances[0]/1000:+.3f} km"),("GR clock difference",f"{components[1]*1e6:+.3f} μs",f"Range equivalent {distances[1]/1000:+.3f} km"),("Net range equivalent",f"{distances[2]/1000:+.3f} km","Clock-derived pseudorange equivalent")])
    xs=np.linspace(0,seconds,120)
    fig=go.Figure()
    for name,rate,color in [("SR clock · cΔt",c["sr_fractional"],"#63a8ff"),("GR clock · cΔt",c["gr_fractional"],"#58d1bd"),("Net clock · cΔt",c["net_fractional"],"#f7bd63")]:fig.add_scatter(x=xs/3600,y=np.array([pseudorange_error(rate*float(t))/1000 for t in xs]),mode="lines",name=name,line=dict(color=color,width=3))
    st.plotly_chart(chart_layout(fig,"Signed range equivalent, cΔt (km)","Accumulated clock-derived range equivalent","Elapsed time (hours)"),width="stretch")
    st.caption("Curves plot the signed range equivalent cΔt for each clock-rate difference. Section C below explains how this sign convention relates to the pseudorange equation.")

    st.markdown("### Background: from clock error to pseudorange")
    net_range_km=pseudorange_error(standard["net_fractional"]*DAY)/1000
    with st.expander("A — How GPS measures distance"):
        st.write("GPS satellites transmit radio signals containing timing information. A receiver compares the signal's transmitted time with its approximate reception time to estimate how long the signal travelled. Multiplying travel time by the speed of light gives an idealized distance.")
        st.latex(r"d=c\,\Delta t")
        st.write("Here d is the idealized signal distance in metres, c is the speed of light in metres per second, and Δt is signal travel time in seconds. For Δt = 0.07 s:")
        st.latex(r"d=299792458\times0.07=20985472.06\ {\rm m}\approx20985\ {\rm km}")
        st.caption("This idealized distance is before clock biases and propagation delays are accounted for.")

    with st.expander("B — What is pseudorange?"):
        st.write("The measured travel time is not exact geometric travel time because the satellite and receiver clocks may differ from GPS system time. With the sign convention used here:")
        st.markdown("- **d** — geometric satellite-to-receiver distance (m)\n- **δt_r** — receiver clock bias (s), contributing **+cδt_r**\n- **δt_s** — satellite clock bias (s), contributing **−cδt_s**\n- **ρ** — measured pseudorange (m)")
        st.latex(r"\rho=d+c(\delta t_r-\delta t_s)")
        st.write("A positive receiver clock bias therefore adds to the pseudorange, while a positive satellite clock bias subtracts from it. A simplified model also includes propagation and remaining measurement errors:")
        st.latex(r"\rho=d+c(\delta t_r-\delta t_s)+I+T+\varepsilon")
        st.write("I is ionospheric delay, T is tropospheric delay, and ε represents remaining measurement errors; each is expressed in metres. It is called a pseudorange because it is a distance-like measurement containing clock and propagation terms, rather than just the geometric distance.")

    with st.expander("C — How relativistic clock errors affect pseudorange"):
        st.write("At the standard GPS orbit, the simplified clock-rate model gives these changes in the satellite clock relative to the ground reference:")
        st.markdown(f"- **SR:** {standard['sr_us_day']:+.3f} μs/day (satellite clock loses time)\n- **GR:** {standard['gr_us_day']:+.3f} μs/day (satellite clock gains time)\n- **Net satellite clock change:** {standard['net_us_day']:+.3f} μs/day")
        st.latex(r"\Delta t_{net}=\Delta t_{SR}+\Delta t_{GR}")
        st.write("This simulator's `pseudorange_error()` uses the signed clock-derived range equivalent cΔt. Thus a positive net satellite clock gain produces a positive value in the simulator's range-equivalent convention:")
        st.latex(r"|\Delta d|=c|\Delta t_{net}|=299792458\times38.453\times10^{-6}\approx11528\ {\rm m}=11.528\ {\rm km/day}")
        st.info(f"Keep three signs distinct: the satellite clock gains {standard['net_us_day']:+.3f} μs/day; the conventional pseudorange satellite-clock term is −cδt_s for a positive satellite clock bias; the magnitude of the equivalent range offset is {net_range_km:+.3f} km/day. The simulator plots signed cΔt, not the −cδt_s measurement-model term.")

    with st.expander("D — From pseudorange to position"):
        st.write("A receiver uses each satellite's known position and one pseudorange measurement to constrain its location. In an unconstrained three-dimensional fix, it solves for x, y, z and receiver clock bias δt_r. At least four independent satellite measurements are required for these four unknowns. This geometric process is called trilateration: distance constraints from multiple satellites intersect to locate the receiver.")

elif page=="Analysis / Experiment Lab":
    title("PARAMETER SWEEP · EXPERIMENT","Analysis / Experiment Lab","Vary altitude and compare your selected circular orbit with the standard GPS reference.")
    if st.button("↺ Restore standard GPS values",key="analysis_reset"):
        st.session_state["analysis_altitude_km"]=20200
    altitude=altitude_control("analysis_altitude_km",maximum=40000)
    c=gps_correction(altitude)
    metric_row([("Orbit speed",f'{c["velocity_m_s"]:,.3f} m/s',"Circular orbit"),("SR",f'{c["sr_us_day"]:+.3f} μs/day',"Motion contribution"),("GR",f'{c["gr_us_day"]:+.3f} μs/day',"Gravity contribution"),("Net range equivalent",f'{pseudorange_error(c["net_fractional"]*DAY)/1000:+.3f} km/day',"Clock-derived equivalent")])
    ref=gps_correction(GPS_ALTITUDE)
    st.markdown("#### Selected orbit versus standard GPS")
    metric_row([("Selected altitude",f'{altitude/1000:,.0f} km',"Current control"),("Standard altitude","20,200 km","Reference"),("Selected net",f'{c["net_us_day"]:+.3f} μs/day',"Current"),("Reference net",f'{ref["net_us_day"]:+.3f} μs/day',"Standard GPS")])
    hs=np.linspace(0,40_000_000,201); sweep=[gps_correction(float(h)) for h in hs]
    fig=go.Figure()
    for key,name,color in [("sr_us_day","SR","#63a8ff"),("gr_us_day","GR","#58d1bd"),("net_us_day","Net","#f7bd63")]:fig.add_scatter(x=hs/1000,y=[x[key] for x in sweep],mode="lines",name=name,line=dict(color=color,width=3))
    fig.add_vline(x=altitude/1000,line_dash="dash",line_color="#f3f7fc",annotation_text="selected")
    st.plotly_chart(chart_layout(fig,"Clock correction (μs/day)","Relativistic components versus altitude","Altitude above Earth's surface (km)"),width="stretch")
    days=st.slider("Clock accumulation window (days)",1,30,7,key="analysis_days")
    ts=np.linspace(0,days*DAY,120); fig2=go.Figure()
    for rate,name,color in [(c["sr_fractional"],"SR","#63a8ff"),(c["gr_fractional"],"GR","#58d1bd"),(c["net_fractional"],"Net","#f7bd63")]:fig2.add_scatter(x=ts/DAY,y=[rate*float(t)*1e6 for t in ts],mode="lines",name=name,line=dict(color=color,width=3))
    st.plotly_chart(chart_layout(fig2,"Accumulated clock difference (μs)","Clock difference builds over time","Elapsed time (days)"),width="stretch")
    st.caption("Circular-orbit speed and weak-field gravity are recalculated at every altitude. Rates are treated as constant over the selected accumulation interval.")

elif page=="Theory & Derivations":
    orbit_ref=circular_orbit(GPS_ALTITUDE)
    deriv_ref=gps_correction(GPS_ALTITUDE)
    range_ref=pseudorange_error(deriv_ref["net_fractional"]*DAY)
    title("GPS RELATIVITY SIMULATOR","Theory & Derivations","Build the GPS clock corrections from orbital mechanics, a light clock, and weak-field gravity.")
    st.write("The derivation compares a satellite clock with a stationary surface reference in a simplified spherical, non-rotating model. Each section introduces the physical idea, derives the equation, and then connects it to the simulator.")
    st.markdown("### A — Reference model and orbital radius")
    st.write(f"The model constants are c = {C:.0f} m/s, GM = {GM:.9e} m³/s², Earth's equatorial radius Rₑ = {EARTH_RADIUS:.0f} m, and standard GPS altitude h = {GPS_ALTITUDE:.0f} m.")
    st.write("Altitude h is measured upward from the chosen Earth surface. Orbital radius r is measured from Earth's centre, so it includes the Earth radius:")
    st.latex(r"r=R_E+h=6378000+20200000=26578000\ {\rm m}")
    st.write("The following derivations use these standard GPS values; the interactive labs allow the parameters to vary.")

    with st.expander("B — Derive circular orbital velocity and period",expanded=True):
        st.write("Newtonian gravity attracts a satellite of mass m toward Earth's centre. For a circular orbit, the required centripetal force has the expression below. Gravity supplies the centripetal acceleration; these are not separate forces to add.")
        st.latex(r"F_{gravity}=\frac{GMm}{r^2},\qquad F_{centripetal}=\frac{mv^2}{r}")
        st.write("Set the gravitational force equal to the force requirement for circular motion, then cancel the nonzero satellite mass m:")
        st.latex(r"\frac{GMm}{r^2}=\frac{mv^2}{r}\quad\Longrightarrow\quad\frac{GM}{r^2}=\frac{v^2}{r}\quad\Longrightarrow\quad\frac{GM}{r}=v^2")
        st.latex(r"v=\sqrt{\frac{GM}{r}}")
        st.write(f"Substituting the reference values gives v = √(3.986004418×10¹⁴ / 26,578,000) = **{orbit_ref['velocity_m_s']:,.3f} m/s**. One orbit covers circumference 2πr at this speed:")
        st.latex(r"T=\frac{2\pi r}{v}")
        st.write(f"T = **{orbit_ref['period_s']:,.0f} s ≈ {orbit_ref['period_s']/3600:.2f} hours**. This calculation assumes a circular orbit and a central spherical gravitational field.")

    with st.expander("C — Derive the special-relativistic correction",expanded=True):
        st.write("Proper time Δτ is time measured by a clock along its own path. Coordinate time Δt is the time interval assigned by the chosen stationary reference frame. For a light clock at rest, two mirrors are separated by distance L; light travels vertically between them in each half-cycle.")
        st.latex(r"c\,\frac{\Delta\tau}{2}=L")
        st.write("For an observer who sees the light clock move horizontally at speed v, the light follows a diagonal path during that half-cycle. The horizontal displacement is vΔt/2, so Pythagoras gives:")
        st.latex(r"\left(c\frac{\Delta t}{2}\right)^2=L^2+\left(v\frac{\Delta t}{2}\right)^2")
        st.write("Substitute L=cΔτ/2 and simplify:")
        st.latex(r"c^2\Delta t^2=c^2\Delta\tau^2+v^2\Delta t^2")
        st.latex(r"\frac{\Delta\tau}{\Delta t}=\sqrt{1-\frac{v^2}{c^2}},\qquad \gamma=\frac{1}{\sqrt{1-v^2/c^2}}")
        st.write("The satellite clock's fractional rate difference from the stationary clock is its rate ratio minus one:")
        st.latex(r"\epsilon_{SR}=\sqrt{1-v^2/c^2}-1")
        st.write("This is negative because for any nonzero v, the square root is less than one. The satellite clock therefore accumulates less proper time in this kinematic comparison. Using the circular-orbit speed:")
        st.latex(r"\epsilon_{SR}\approx-8.3434\times10^{-11},\qquad\Delta t_{SR}=\epsilon_{SR}\times86400\ {\rm s}")
        st.write(f"The result is **{deriv_ref['sr_us_day']:+.3f} μs/day**. Numerically, the code uses x=v²/c² and an equivalent stable form to avoid cancellation when x is tiny:")
        st.latex(r"\epsilon_{SR}=-\frac{x}{1+\sqrt{1-x}},\qquad x=\frac{v^2}{c^2}")

    with st.expander("D — Derive the weak-field gravitational correction",expanded=True):
        st.write("With gravitational potential zero at infinity, the Newtonian potential is negative near Earth. At larger r, Φ is less negative (closer to zero), corresponding to a weaker gravitational field:")
        st.latex(r"\Phi=-\frac{GM}{r}")
        st.write("For a stationary clock in the ideal Schwarzschild spacetime, the clock rate relative to coordinate time is:")
        st.latex(r"\frac{d\tau}{dt}=\sqrt{1-\frac{2GM}{rc^2}}")
        st.write("For Earth, 2GM/(rc²) is very small. Using √(1−x) ≈ 1−x/2 for small x gives the weak-field limit:")
        st.latex(r"\frac{d\tau}{dt}\approx1-\frac{GM}{rc^2}=1+\frac{\Phi}{c^2}")
        st.write("Compare two stationary clocks at the satellite radius and the Earth's surface. To first order, divide their rates and retain the leading difference:")
        st.latex(r"\left(\frac{d\tau_S}{dt}\right)\approx1+\frac{\Phi_S}{c^2},\quad\left(\frac{d\tau_E}{dt}\right)\approx1+\frac{\Phi_E}{c^2},\quad\frac{d\tau_S}{d\tau_E}\approx1+\frac{\Phi_S-\Phi_E}{c^2}")
        st.latex(r"\epsilon_{GR}=\frac{\Phi_S-\Phi_E}{c^2}=\frac{GM}{c^2}\left(\frac{1}{R_E}-\frac{1}{r}\right)")
        st.write("At positive altitude r>Rₑ, the term in parentheses is positive, so the higher satellite clock runs faster from the gravitational contribution. For the reference orbit:")
        st.latex(r"\epsilon_{GR}\approx+5.2850\times10^{-10},\qquad\Delta t_{GR}=\epsilon_{GR}\times86400\ {\rm s}")
        st.write(f"The result is **{deriv_ref['gr_us_day']:+.3f} μs/day**. The Schwarzschild expression above is for a stationary clock; it is not the complete rate formula for a moving satellite. This simulator separately calculates the leading kinematic SR contribution and weak-field gravitational contribution, then combines them to first order.")

    with st.expander("E — Combine the effects",expanded=True):
        st.write("The educational model adds the leading fractional rate differences. Products between corrections of order 10⁻¹⁰ are of order 10⁻²⁰ and are neglected:")
        st.latex(r"\epsilon_{net}\approx\epsilon_{SR}+\epsilon_{GR}=-8.3434\times10^{-11}+5.2850\times10^{-10}\approx+4.45066\times10^{-10}")
        st.latex(r"\Delta t_{net}=\epsilon_{net}\times86400\ {\rm s}\approx+38.453\ {\rm \mu s/day}")
        st.write("SR slows the moving satellite clock; GR speeds it relative to the ground. At standard GPS altitude, GR dominates, so the net satellite clock rate is faster.")

    st.markdown("### F — Numerical summary")
    metric_row([("Orbital radius",f'{orbit_ref["radius_m"]:,.0f} m',"r = Rₑ + h"),("Orbital velocity",f'{orbit_ref["velocity_m_s"]:,.3f} m/s',"Circular orbit"),("Orbital period",f'{orbit_ref["period_s"]/3600:.2f} h',"About 11.98 hours"),("Range magnitude",f'{abs(range_ref)/1000:.3f} km/day',"|cΔt_net|")])
    metric_row([("SR",f'{deriv_ref["sr_us_day"]:+.3f} μs/day',"Kinematic contribution"),("GR",f'{deriv_ref["gr_us_day"]:+.3f} μs/day',"Gravitational contribution"),("Net",f'{deriv_ref["net_us_day"]:+.3f} μs/day',"First-order sum")])

    st.markdown("### G — Continue exploring")
    st.markdown("- **Orbital mechanics and net correction:** Combined GPS Correction\n- **Speed what-if experiments for the SR result:** Special Relativity Lab\n- **Altitude dependence of the GR result:** General Relativity Lab\n- **Clock-to-range conversion:** Positioning Error")

else:
    title("REFERENCE · THEORY","Theory & Assumptions","A compact derivation of what the simulator computes and what it leaves out.")
    st.markdown("### Proper time and coordinate time")
    st.write("Proper time τ is the time recorded by a clock along its own path. Coordinate time is the common reference used to compare separated clocks in this simplified model. The simulator computes the satellite clock's rate relative to a stationary ground clock.")
    st.markdown("### Why the effects have opposite signs")
    st.write("Motion reduces a moving clock's rate: ε_SR = √(1−v²/c²)−1, which is negative. Gravitational potential is Φ=−GM/r. At greater radius the potential is less negative, so the weak-field clock rate is higher: ε_GR=(GM/c²)(1/Rₑ−1/r), which is positive.")
    st.markdown("### Orbit and net model")
    st.latex(r"r=R_E+h,\qquad v=\sqrt{GM/r},\qquad T=2\pi r/v,\qquad \epsilon_{net}=\epsilon_{SR}+\epsilon_{GR}")
    st.write("Circular orbit comes from equating GMm/r² with mv²/r. The weak-field approximation is appropriate here because Earth's gravitational potential per unit mass divided by c² is very small. The net expression adds leading-order rate differences.")
    st.markdown("### Standard GPS reference")
    metric_row([("SR",f'{standard["sr_us_day"]:+.3f} μs/day',"Expected about −7.209"),("GR",f'{standard["gr_us_day"]:+.3f} μs/day',"Expected about +45.662"),("Net",f'{standard["net_us_day"]:+.3f} μs/day',"Expected about +38.453"),("Pseudorange",f'{pseudorange_error(standard["net_fractional"]*DAY)/1000:+.3f} km/day',"Equivalent range offset")])
    st.markdown("### Assumptions and limitations")
    st.write("The core model uses a spherical Earth, circular orbit, standard GM, weak-field gravitational time dilation, a stationary non-rotating ground reference clock, and first-order addition of SR and GR clock-rate corrections.")
    st.write("It excludes orbital eccentricity, Earth's rotation and geoid, Sagnac correction, signal propagation effects, atmospheric delays, multipath, satellite orbit errors, receiver clock bias, and other operational GPS corrections. Sagnac is a signal-propagation correction associated with Earth's rotating reference frame; it is distinct from gravitational clock-rate correction.")
    st.write("Operational GPS systems account for additional effects and pre-adjust satellite clock frequencies. This educational simulator is not a complete operational GPS receiver. The range-equivalent clock offset is not the actual final receiver position error.")
