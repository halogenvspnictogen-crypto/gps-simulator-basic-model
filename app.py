"""GPS Relativity Simulator — interactive Streamlit teaching laboratory."""
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from physics.constants import C, EARTH_RADIUS, GPS_ALTITUDE, DAY
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
h1,h2,h3{color:#f3f7fc} p,li{color:#d2dce8}
</style>""", unsafe_allow_html=True)

PAGES = ["Overview", "Special Relativity Lab", "General Relativity Lab", "Combined GPS Correction", "Positioning Error", "Analysis / Experiment Lab", "Theory & Assumptions"]
with st.sidebar:
    st.markdown("## 🛰️ GPS Relativity")
    page = st.radio("Laboratory", PAGES, label_visibility="collapsed")
    st.divider()
    st.caption("REFERENCE ORBIT")
    st.metric("Altitude", "20,200 km")
    st.caption("Spherical Earth · circular orbit · first-order clock-rate model")

def chart_layout(fig, ytitle, title=None):
    fig.update_layout(template="plotly_dark", title=title, height=390, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(9,17,29,.6)",
                      margin=dict(l=20,r=20,t=55,b=25), yaxis_title=ytitle, font=dict(color="#d8e3ef"), legend=dict(orientation="h", y=1.12))
    fig.update_xaxes(gridcolor="#26384c")
    fig.update_yaxes(gridcolor="#26384c", zerolinecolor="#8aa0b8")
    return fig

def correction_chart(c):
    fig=go.Figure()
    for name,key,color in [("Special Relativity","sr_us_day","#63a8ff"),("General Relativity","gr_us_day","#58d1bd"),("Net","net_us_day","#f7bd63")]:
        fig.add_bar(name=name,x=[name],y=[c[key]],marker_color=color,text=[f"{c[key]:+.3f}"],textposition="outside")
    fig.update_layout(barmode="group",showlegend=False)
    return chart_layout(fig,"Clock correction (μs/day)","Daily clock-rate difference")

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
    st.plotly_chart(correction_chart(standard),use_container_width=True)
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
    velocity=st.slider("Satellite speed (km/s)",0.0,30.0,round(standard["velocity_m_s"]/1000,3),0.01,key="sr_velocity")*1000
    frac=sr_fractional_rate(velocity); rate=sr_daily_us(velocity)
    metric_row([("Speed",f"{velocity:,.1f} m/s","Input speed"),("Lorentz factor γ",f"{lorentz_factor(velocity):.12f}","γ = 1/√(1−v²/c²)"),("Fractional rate",f"{frac:.6e}","Moving clock rate minus reference rate"),("Daily difference",f"{rate:+.4f} μs/day","Negative means the moving clock loses time")])
    speeds=np.linspace(0,30_000,301); vals=np.array([sr_daily_us(float(v)) for v in speeds])
    fig=go.Figure(go.Scatter(x=speeds/1000,y=vals,mode="lines",line=dict(color="#63a8ff",width=3),name="SR correction"));fig.add_vline(x=velocity/1000,line_dash="dash",line_color="#f7bd63")
    st.plotly_chart(chart_layout(fig,"SR correction (μs/day)","Motion makes the clock run slower"),use_container_width=True)

elif page=="General Relativity Lab":
    title("ISOLATED EFFECT · GRAVITY","General Relativity Lab","Compare weak-field clock rates at Earth's surface and above it.")
    st.latex(r"\Phi=-GM/r,\quad d\tau/dt\approx1+\Phi/c^2,\quad \epsilon_{GR}=\frac{GM}{c^2}(1/R_E-1/r)")
    st.write("The gravitational potential becomes less negative with altitude. A clock higher in the gravitational field accumulates more time relative to the surface clock, so this differential correction is positive.")
    altitude=altitude_control("gr_altitude_km")
    radius=EARTH_RADIUS+altitude; frac=gr_fractional_rate(altitude); rate=gr_daily_us(altitude)
    metric_row([("Altitude",f"{altitude/1000:,.0f} km","Above the reference surface"),("Surface potential",f"{gravitational_potential(EARTH_RADIUS):.4e} J/kg","Φ = −GM/Rₑ"),("Satellite potential",f"{gravitational_potential(radius):.4e} J/kg","Φ = −GM/r"),("Daily difference",f"{rate:+.4f} μs/day","Positive means higher clock gains time")])
    hs=np.linspace(0,40_000_000,301); ys=np.array([gr_daily_us(float(h)) for h in hs])
    fig=go.Figure(go.Scatter(x=hs/1000,y=ys,mode="lines",line=dict(color="#58d1bd",width=3),name="GR correction"));fig.add_vline(x=altitude/1000,line_dash="dash",line_color="#f7bd63")
    st.plotly_chart(chart_layout(fig,"GR correction (μs/day)","Higher altitude means a faster clock"),use_container_width=True)
    st.caption("The horizontal axis is altitude above the spherical surface; the comparison is differential, so it is zero at zero altitude.")

elif page=="Combined GPS Correction":
    title("CENTRAL RESULT · CIRCULAR ORBIT","Combined GPS Clock Correction","The orbit model supplies velocity; both clock effects are then added at first order.")
    if st.button("↺ Restore standard GPS orbit",key="combined_reset"):
        st.session_state["combined_altitude_km"]=20200
    altitude=altitude_control("combined_altitude_km")
    c=gps_correction(altitude)
    metric_row([("Orbital radius",f'{c["radius_m"]/1000:,.0f} km',"Rₑ + altitude"),("Circular speed",f'{c["velocity_m_s"]:,.3f} m/s',"v = √(GM/r)"),("Orbital period",f'{c["period_s"]/3600:.3f} h',"T = 2πr/v"),("Net rate",f'{c["net_us_day"]:+.3f} μs/day',"Satellite clock gains for the standard GPS orbit")])
    st.plotly_chart(correction_chart(c),use_container_width=True)
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
    st.latex(r"\Delta d=c\,\Delta t")
    st.write("A timing offset changes the distance inferred from a signal's travel time. This pseudorange-equivalent value is not the receiver's final position error: real receivers estimate their clock bias and position from signals from multiple satellites.")
    c=gps_correction(GPS_ALTITUDE); hours=st.select_slider("Elapsed time",options=[1,24,24*7,24*30],value=24,format_func=lambda h:{1:"1 hour",24:"1 day",168:"7 days",720:"30 days"}[h],key="duration_hours")
    seconds=hours*3600; labels=["Special Relativity","General Relativity","Net"]
    components=[c["sr_fractional"]*seconds,c["gr_fractional"]*seconds,c["net_fractional"]*seconds]
    distances=[pseudorange_error(x) for x in components]
    metric_row([("Elapsed",f"{hours:g} h","Accumulation period"),("SR clock difference",f"{components[0]*1e6:+.3f} μs",f"Range equivalent {distances[0]/1000:+.3f} km"),("GR clock difference",f"{components[1]*1e6:+.3f} μs",f"Range equivalent {distances[1]/1000:+.3f} km"),("Net range equivalent",f"{distances[2]/1000:+.3f} km","Clock-derived pseudorange equivalent")])
    xs=np.linspace(0,seconds,120)
    fig=go.Figure()
    for name,rate,color in [(labels[0],c["sr_fractional"],"#63a8ff"),(labels[1],c["gr_fractional"],"#58d1bd"),(labels[2],c["net_fractional"],"#f7bd63")]:fig.add_scatter(x=xs/3600,y=np.array([pseudorange_error(rate*float(t))/1000 for t in xs]),mode="lines",name=name,line=dict(color=color,width=3))
    st.plotly_chart(chart_layout(fig,"Pseudorange equivalent (km)","Clock-derived range offset accumulates linearly"),use_container_width=True)
    st.caption("Range equivalents use cΔt. Real navigation solutions combine measurements and estimate receiver clock bias; this plot is not a receiver position simulation.")

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
    st.plotly_chart(chart_layout(fig,"Clock correction (μs/day)","Relativistic components versus altitude"),use_container_width=True)
    days=st.slider("Clock accumulation window (days)",1,30,7,key="analysis_days")
    ts=np.linspace(0,days*DAY,120); fig2=go.Figure()
    for rate,name,color in [(c["sr_fractional"],"SR","#63a8ff"),(c["gr_fractional"],"GR","#58d1bd"),(c["net_fractional"],"Net","#f7bd63")]:fig2.add_scatter(x=ts/DAY,y=[rate*float(t)*1e6 for t in ts],mode="lines",name=name,line=dict(color=color,width=3))
    st.plotly_chart(chart_layout(fig2,"Accumulated clock difference (μs)","Clock difference builds over time"),use_container_width=True)
    st.caption("Circular-orbit speed and weak-field gravity are recalculated at every altitude. Rates are treated as constant over the selected accumulation interval.")

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
