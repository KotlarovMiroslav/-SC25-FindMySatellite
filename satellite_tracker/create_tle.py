"""
TLE_from_Waypoints.py

Refactored, complete script that converts 3+ lidar+stepper+servo waypoints
(range, az_deg, el_deg, iso-utc) measured at a fixed ground site into a
syntactically-correct TLE. This version automatically selects the solver:
- 3 waypoints -> Herrick–Gibbs velocity estimate
- >3 waypoints -> least-squares linear fit for velocity (per-component)

Features:
- Full ECEF <-> ECI handling using GMST (sufficient for demo/teaching)
- Geodetic WGS84 site definition (default Sofia, Bulgaria)
- Optionally "map_to_space" to keep measured plane but force realistic LEO
  semi-major axis (e.g. 500 km) and small eccentricity for use with SGP4
- Proper TLE formatting: field widths, BSTAR small realistic value, and
  correct checksums for both lines
- Includes a powerful validation function to re-format and fix TLE checksums.
- Clear example usage block at bottom; replace with your logs to test.

Limitations / notes:
- This is an educational tool. Waypoints a few meters apart will produce
  physically meaningless orbital elements unless map_to_space=True.
- The least-squares fit is linear-in-time per coordinate (works if motion is
  approximately constant velocity during the measurement window).
- No high-precision Earth orientation (no polar motion/nutation) — good
  enough for short demos.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Tuple
import math
import re
from datetime import datetime, timezone

# ---------------------------- CONFIG ----------------------------
DEFAULT_LAT = 42.6977
DEFAULT_LON = 23.3219
DEFAULT_ALT_M = 550.0
DEFAULT_TARGET_ALT_KM = 500.0
DEFAULT_BSTAR = 1.2345e-4

# ---------------------------- Constants ----------------------------
WGS84_A = 6378137.0
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = WGS84_F * (2 - WGS84_F)
MU_EARTH = 398600.4418
R_EARTH_KM = 6378.137

# ---------------------------- Utilities ----------------------------

def _to_datetime_utc(ts: str) -> datetime:
    if ts.endswith("Z"):
        dt = datetime.fromisoformat(ts[:-1]).replace(tzinfo=timezone.utc)
    else:
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
    return dt

def _julian_date(dt: datetime) -> float:
    year, month = dt.year, dt.month
    day = dt.day + (dt.hour + (dt.minute + (dt.second + dt.microsecond / 1e6) / 60.0) / 60.0) / 24.0
    if month <= 2:
        year -= 1
        month += 12
    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)
    return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5

def _gmst_rad(dt: datetime) -> float:
    JD = _julian_date(dt)
    T = (JD - 2451545.0) / 36525.0
    gmst_s = 67310.54841 + (876600.0 * 3600 + 8640184.812866) * T + 0.093104 * T * T - 6.2e-6 * T**3
    return math.radians((gmst_s / 240.0) % 360.0)

# ---------------------------- Frames ----------------------------

def geodetic_to_ecef(lat_deg: float, lon_deg: float, alt_m: float) -> Tuple[float, float, float]:
    lat_rad, lon_rad = math.radians(lat_deg), math.radians(lon_deg)
    sin_lat, cos_lat = math.sin(lat_rad), math.cos(lat_rad)
    N = WGS84_A / math.sqrt(1 - WGS84_E2 * sin_lat * sin_lat)
    x = (N + alt_m) * cos_lat * math.cos(lon_rad)
    y = (N + alt_m) * cos_lat * math.sin(lon_rad)
    z = (N * (1 - WGS84_E2) + alt_m) * sin_lat
    return x, y, z

def enu_to_ecef_matrix(lat_deg: float, lon_deg: float) -> List[List[float]]:
    lat_rad, lon_rad = math.radians(lat_deg), math.radians(lon_deg)
    sL, cL = math.sin(lat_rad), math.cos(lat_rad)
    sl, cl = math.sin(lon_rad), math.cos(lon_rad)
    return [
        [-sl, -sL * cl, cL * cl],
        [cl, -sL * sl, cL * sl],
        [0.0, cL, sL],
    ]

def ecef_to_eci(ecef: Tuple[float, float, float], dt: datetime) -> Tuple[float, float, float]:
    x, y, z = ecef
    theta = _gmst_rad(dt)
    c, s = math.cos(theta), math.sin(theta)
    return c * x - s * y, s * x + c * y, z

# ---------------------------- Local spherical ----------------------------

def spherical_local_to_enu(R_m: float, az_deg: float, el_deg: float) -> Tuple[float, float, float]:
    az_rad, el_rad = math.radians(az_deg), math.radians(el_deg)
    E = R_m * math.cos(el_rad) * math.sin(az_rad)
    N = R_m * math.cos(el_rad) * math.cos(az_rad)
    U = R_m * math.sin(el_rad)
    return E, N, U

# ---------------------------- Vector helpers ----------------------------

def vadd(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def vdot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def vxs(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def vnorm(a): return math.sqrt(vdot(a, a))
def vsmul(s, a): return (s * a[0], s * a[1], s * a[2])
def vsub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

# ---------------------------- Orbit Determination ----------------------------

def herrick_gibbs(r1, r2, r3, t1, t2, t3):
    dt21 = (t2 - t1).total_seconds()
    dt31 = (t3 - t1).total_seconds()
    dt32 = (t3 - t2).total_seconds()
    term1 = vsmul(-dt32 / (dt21 * dt31), r1)
    term2 = vsmul((dt32 - dt21) / (dt21 * dt32), r2)
    term3 = vsmul(dt21 / (dt31 * dt32), r3)
    return vadd(vadd(term1, term2), term3)

def least_squares_velocity(r_list, t_list):
    try:
        import numpy as np
    except ImportError:
        raise ImportError("numpy is required for least-squares fit. Please install it: pip install numpy")
    
    t_sec = np.array([(t - t_list[0]).total_seconds() for t in t_list])
    r_arr = np.array(r_list)
    vs = [np.polyfit(t_sec, r_arr[:, dim], 1)[0] for dim in range(3)]
    return tuple(vs)

# ---------------------------- RV -> COE ----------------------------
@dataclass
class OrbitalElements:
    a_km: float; e: float; i_deg: float; raan_deg: float; argp_deg: float; nu_deg: float

def rv_to_coe(r_km, v_km_s) -> OrbitalElements:
    R = vnorm(r_km)
    V = vnorm(v_km_s)
    h = vxs(r_km, v_km_s)
    H = vnorm(h)
    n = vxs((0, 0, 1), h)
    N = vnorm(n)
    
    e_vec = vsub(vsmul((V*V - MU_EARTH/R)/MU_EARTH, r_km), vsmul(vdot(r_km, v_km_s)/MU_EARTH, v_km_s))
    e = vnorm(e_vec)
    
    eps = V*V/2 - MU_EARTH/R
    a = -MU_EARTH/(2*eps) if abs(eps) > 1e-9 else float('inf')
    
    i = math.degrees(math.acos(h[2]/H)) if H > 1e-9 else 0.0
    
    raan = math.degrees(math.acos(n[0]/N)) if N > 1e-9 else 0.0
    if n[1] < 0: raan = 360.0 - raan
    
    argp = math.degrees(math.acos(vdot(n, e_vec)/(N*e))) if N > 1e-9 and e > 1e-9 else 0.0
    if e_vec[2] < 0: argp = 360.0 - argp
        
    nu = math.degrees(math.acos(vdot(e_vec, r_km)/(e*R))) if e > 1e-9 else 0.0
    if vdot(r_km, v_km_s) < 0: nu = 360.0 - nu
        
    return OrbitalElements(a, e, i, raan, argp, nu)

# ---------------------------- Anomalies & TLE Formatting ----------------------------

def mean_from_true(nu_deg: float, e: float) -> float:
    nu_rad = math.radians(nu_deg)
    E_rad = math.atan2(math.sqrt(1 - e * e) * math.sin(nu_rad), e + math.cos(nu_rad))
    M_rad = E_rad - e * math.sin(E_rad)
    return math.degrees(M_rad) % 360.0

def _tle_checksum(line_body: str) -> str:
    return str((sum(int(c) for c in line_body if c.isdigit()) + line_body.count('-')) % 10)

def _epoch_tle(dt: datetime) -> str:
    year = dt.year % 100
    doy = (dt - datetime(dt.year, 1, 1, tzinfo=timezone.utc)).total_seconds() / 86400.0 + 1.0
    return f"{year:02d}{doy:012.8f}"

def _bstar_tle(b: float) -> str:
    if b == 0.0: return " 00000-0"
    sgn = ' ' if b > 0 else '-'
    b_abs = abs(b)
    exp = math.floor(math.log10(b_abs))
    mant = int(round(b_abs / (10**exp) * 10000))
    return f"{sgn}{mant:05d}{exp:+d}".replace('+', '')

def build_tle(coe: OrbitalElements, epoch: datetime, satnum=99999, intldesg='25001A', bstar=DEFAULT_BSTAR, elset=1, revnum=1) -> Tuple[str, str]:
    e = max(0.0, min(0.9999999, coe.e))
    mean_motion_rev_day = math.sqrt(MU_EARTH / abs(coe.a_km)**3) * 86400 / (2 * math.pi) if coe.a_km > 0 else 0
    
    line1_core = (f"1 {satnum:05d}U {intldesg:<8} {_epoch_tle(epoch)} "
                  f".00000000  00000-0{_bstar_tle(bstar)} 0 {min(elset, 9999):>4}")
    line2_core = (f"2 {satnum:05d} {coe.i_deg:8.4f} {coe.raan_deg:8.4f} {f'{e:.7f}'[2:]:7} "
                  f"{coe.argp_deg:8.4f} {mean_from_true(coe.nu_deg, e):8.4f} "
                  f"{mean_motion_rev_day:11.8f}{revnum:<5}")

    return line1_core + _tle_checksum(line1_core), line2_core + _tle_checksum(line2_core)

# ---------------------------- NEW: TLE Validation & Correction Function ----------------------------

def validate_and_correct_tle(line1: str, line2: str) -> Tuple[str, str]:
    """
    Parses, reformats, and corrects the checksums of a two-line element set.
    This ensures the final TLE is syntactically correct.
    """
    print("Running TLE validation and correction...")
    
    # --- Line 1 Parsing and Reformatting ---
    satnum1         = line1[2:7]
    classification  = line1[7:8].strip() or 'U'
    intldesg        = line1[9:17]
    epoch           = line1[18:32]
    mean_motion_dot = line1[33:43]
    mean_motion_dot2= line1[44:52]
    bstar           = line1[53:61]
    ephem_type      = line1[62:63].strip() or '0'
    elset_num       = line1[64:68]

    line1_reformatted = (
        f"1 {satnum1} {classification}{intldesg} {epoch} {mean_motion_dot} "
        f"{mean_motion_dot2}{bstar} {ephem_type} {elset_num.strip():>4}"
    )
    
    # --- Line 2 Parsing and Reformatting ---
    satnum2         = line2[2:7]
    inclination     = float(line2[8:16])
    raan            = float(line2[17:25])
    eccentricity    = line2[26:33] # Keep as string
    arg_perigee     = float(line2[34:42])
    mean_anomaly    = float(line2[43:51])
    mean_motion     = float(line2[52:63])
    rev_num         = line2[63:68]

    line2_reformatted = (
        f"2 {satnum2} {inclination:8.4f} {raan:8.4f} {eccentricity:7} "
        f"{arg_perigee:8.4f} {mean_anomaly:8.4f} {mean_motion:11.8f}{rev_num.strip():<5}"
    )
    
    # --- Checksum Calculation and Finalization ---
    final_line1 = line1_reformatted + _tle_checksum(line1_reformatted)
    final_line2 = line2_reformatted + _tle_checksum(line2_reformatted)
    
    # --- Report Corrections ---
    corrections = []
    if final_line1 != line1.rstrip():
        corrections.append(f"Line 1 was reformatted or its checksum was corrected.")
    if final_line2 != line2.rstrip():
        corrections.append(f"Line 2 was reformatted or its checksum was corrected.")
        
    if not corrections:
        print("TLE validation passed: No issues found.")
    else:
        print("TLE validation found issues and corrected them:")
        for msg in corrections:
            print(f"- {msg}")
            
    return final_line1, final_line2

# ---------------------------- Main Entry ----------------------------

def generate_tle_from_waypoints(waypoints, sensor_lat_deg=DEFAULT_LAT, sensor_lon_deg=DEFAULT_LON, sensor_alt_m=DEFAULT_ALT_M, **kwargs) -> Tuple[str, str, OrbitalElements]:
    wps = list(waypoints)
    if len(wps) < 3: raise ValueError("Need at least 3 waypoints")

    site_ecef_m = geodetic_to_ecef(sensor_lat_deg, sensor_lon_deg, sensor_alt_m)
    rot_enu_to_ecef = enu_to_ecef_matrix(sensor_lat_deg, sensor_lon_deg)
    
    eci_positions_km, times_utc = [], []
    for Rm, az, el, ts in wps:
        enu_m = spherical_local_to_enu(Rm, az, el)
        ecef_offset_m = (
            vdot([rot_enu_to_ecef[0][0], rot_enu_to_ecef[1][0], rot_enu_to_ecef[2][0]], enu_m),
            vdot([rot_enu_to_ecef[0][1], rot_enu_to_ecef[1][1], rot_enu_to_ecef[2][1]], enu_m),
            vdot([rot_enu_to_ecef[0][2], rot_enu_to_ecef[1][2], rot_enu_to_ecef[2][2]], enu_m),
        )
        object_ecef_m = vadd(site_ecef_m, ecef_offset_m)
        dt = _to_datetime_utc(ts)
        object_eci_m = ecef_to_eci(object_ecef_m, dt)
        
        eci_positions_km.append(vsmul(1/1000.0, object_eci_m))
        times_utc.append(dt)
        
    if len(wps) == 3:
        v_km_s = herrick_gibbs(*eci_positions_km, *times_utc)
        r_km, epoch = eci_positions_km[1], times_utc[1]
    else:
        v_km_s = least_squares_velocity(eci_positions_km, times_utc)
        mid_idx = len(wps)//2
        r_km, epoch = eci_positions_km[mid_idx], times_utc[mid_idx]
        
    coe = rv_to_coe(r_km, v_km_s)
    
    if kwargs.get('map_to_space', False):
        coe.a_km = R_EARTH_KM + kwargs.get('target_alt_km', DEFAULT_TARGET_ALT_KM)
        coe.e = kwargs.get('small_e', 0.001)
        
    tle_build_kwargs = {k:v for k,v in kwargs.items() if k in ['satnum', 'intldesg', 'bstar', 'elset', 'revnum']}
    l1, l2 = build_tle(coe, epoch, **tle_build_kwargs)
    return l1, l2, coe

# ---------------------------- Example Usage ----------------------------
if __name__ == "__main__":
    waypoints_example = [
        (8.0, 10.0, 45.0, "2025-08-14T12:00:00.000Z"),
        (8.5, 40.0, 90.0,   "2025-08-14T12:00:10.000Z"),
        (10.0, 80.0, 30.0,  "2025-08-14T12:00:20.000Z"),
    ]

    print("--- Generating TLE ---")
    line1_raw, line2_raw, coe_final = generate_tle_from_waypoints(
        waypoints_example,
        map_to_space=True,
        target_alt_km=500.0,
        elset=999
    )
    # 1. Generate the TLE from waypoints
    print("--- Generating TLE ---")
    line1_raw, line2_raw, coe_final = generate_tle_from_waypoints(
        waypoints_example,
        map_to_space=True,
        target_alt_km=500.0,
        elset=999
    )
    print("Raw generated TLE (before validation):")
    print(line1_raw)
    print(line2_raw)
    print("\n--- Validating and Correcting TLE ---")

    # 2. Validate and correct the generated TLE
    line1_final, line2_final = validate_and_correct_tle(line1_raw, line2_raw)
    
    print("\n--- Final, Validated TLE ---")
    print(line1_final)
    print(line2_final)
    
    print("\nFinal Orbital Elements used for TLE:")
    print(coe_final)