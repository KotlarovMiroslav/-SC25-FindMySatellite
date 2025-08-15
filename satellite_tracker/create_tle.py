"""
Generate a (demo/educational) TLE from 3+ LiDAR+servo+stepper waypoints.

Inputs per waypoint: (range_m, az_deg, el_deg, timestamp_iso8601_utc)
- az_deg: 0° = North, positive clockwise toward East (standard azimuth)
- el_deg: 0° = horizon, +90° = zenith
- range_m: slant range from the sensor in meters
- timestamp: e.g. "2025-08-14T12:00:00.000Z" or without Z but in UTC

Assumes sensor fixed at Sofia, Bulgaria by default (can be changed).

Notes:
- This is for learning. With noisy/short-baseline measurements, the orbit fit is rough.
- We use Herrick–Gibbs to estimate v2 at the middle time from 3 position vectors.
- We convert ECEF -> ECI using GMST (simple model). No nutation/polar motion.
- If map_to_space=True, we keep the *plane* (i, RAAN, argp) but force a target
  semi-major axis (e.g., circular 500 km altitude) and set a small eccentricity.
- Output is a syntactically valid TLE (69-char lines) usable by SGP4, but the
  physical fidelity depends on your inputs and the simplifications here.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Tuple
import math
from datetime import datetime, timezone

# ---------------------------- Constants ----------------------------
WGS84_A = 6378137.0  # m
WGS84_F = 1.0 / 298.257223563
WGS84_E2 = WGS84_F * (2 - WGS84_F)
OMEGA_EARTH = 7.2921150e-5  # rad/s (not directly used; GMST used instead)
MU_EARTH = 398600.4418  # km^3/s^2 (for orbital elements)
R_EARTH_KM = 6378.137  # km (equatorial radius)

# ---------------------------- Utility ----------------------------

def _to_datetime_utc(ts: str) -> datetime:
    # Allow 'Z' or no tz -> assume UTC
    if ts.endswith("Z"):
        ts = ts[:-1]
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt

# Julian date utilities (UTC -> JD)
def _julian_date(dt: datetime) -> float:
    # Algorithm from Vallado (simplified for UTC)
    year = dt.year
    month = dt.month
    day = dt.day + (dt.hour + (dt.minute + (dt.second + dt.microsecond/1e6)/60.0)/60.0)/24.0
    if month <= 2:
        year -= 1
        month += 12
    A = math.floor(year/100)
    B = 2 - A + math.floor(A/4)
    JD = math.floor(365.25*(year + 4716)) + math.floor(30.6001*(month + 1)) + day + B - 1524.5
    return JD

# GMST from JD (IAU 1982 style, sufficient for demo)
def _gmst_rad(dt: datetime) -> float:
    JD = _julian_date(dt)
    T = (JD - 2451545.0)/36525.0
    gmst = 67310.54841 + (876600.0*3600 + 8640184.812866)*T + 0.093104*T*T - 6.2e-6*T**3
    gmst = math.radians((gmst/240.0) % 360.0)  # convert sec -> deg -> rad, wrap
    return gmst

# ---------------------------- Frames ----------------------------

def geodetic_to_ecef(lat_deg: float, lon_deg: float, alt_m: float) -> Tuple[float,float,float]:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    sin_lat = math.sin(lat)
    cos_lat = math.cos(lat)
    N = WGS84_A / math.sqrt(1 - WGS84_E2 * sin_lat*sin_lat)
    x = (N + alt_m) * cos_lat * math.cos(lon)
    y = (N + alt_m) * cos_lat * math.sin(lon)
    z = (N*(1 - WGS84_E2) + alt_m) * sin_lat
    return x, y, z

# ENU -> ECEF rotation matrix at site (row-major)
def enu_to_ecef_matrix(lat_deg: float, lon_deg: float) -> List[List[float]]:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    sL, cL = math.sin(lat), math.cos(lat)
    sl, cl = math.sin(lon), math.cos(lon)
    # Rows take ENU to ECEF
    return [
        [-sl,             cl,              0.0],
        [-sL*cl,         -sL*sl,           cL ],
        [ cL*cl,          cL*sl,           sL ],
    ]

# ECEF -> ECI using GMST rotation about z: ECI = R3(-gmst) * ECEF

def ecef_to_eci(ecef: Tuple[float,float,float], dt: datetime) -> Tuple[float,float,float]:
    x, y, z = ecef
    theta = _gmst_rad(dt)
    c, s = math.cos(-theta), math.sin(-theta)
    X = c*x - s*y
    Y = s*x + c*y
    Z = z
    return X, Y, Z

# ---------------------------- Local spherical ----------------------------

def spherical_local_to_enu(R_m: float, az_deg: float, el_deg: float) -> Tuple[float,float,float]:
    # az: 0=N, 90=E; el: 0=horizon, +90=up
    az = math.radians(az_deg)
    el = math.radians(el_deg)
    E = R_m * math.cos(el) * math.sin(az)
    N = R_m * math.cos(el) * math.cos(az)
    U = R_m * math.sin(el)
    return E, N, U

# ---------------------------- Vector helpers ----------------------------

def vadd(a,b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def vsub(a,b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def vdot(a,b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

def vxs(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def vnorm(a): return math.sqrt(vdot(a,a))

def vsmul(s,a): return (s*a[0], s*a[1], s*a[2])

# ---------------------------- Herrick–Gibbs ----------------------------

def herrick_gibbs(r1, r2, r3, t1, t2, t3):
    """Estimate v2 at r2 using Herrick–Gibbs (Vallado). r in km, t in seconds.
    """
    dt21 = t2 - t1
    dt31 = t3 - t1
    dt32 = t3 - t2
    term1 = vsmul(-dt32/(dt21*dt31), r1)
    term2 = vsmul((dt32 - dt21)/(dt21*dt32), r2)
    term3 = vsmul(dt21/(dt31*dt32), r3)
    v2 = vsmul(1.0, vadd(vadd(term1, term2), term3))
    return v2

# ---------------------------- RV -> COE ----------------------------
@dataclass
class OrbitalElements:
    a_km: float
    e: float
    i_deg: float
    raan_deg: float
    argp_deg: float
    nu_deg: float  # true anomaly at epoch


def rv_to_coe(r_km, v_km_s) -> OrbitalElements:
    r = r_km
    v = v_km_s
    R = vnorm(r)
    V = vnorm(v)
    h = vxs(r, v)
    H = vnorm(h)
    k = (0.0, 0.0, 1.0)
    n = vxs(k, h)
    N = vnorm(n)
    e_vec = vsub(vsmul((V*V - MU_EARTH/R)/MU_EARTH, r), vsmul(vdot(r,v)/MU_EARTH, v))
    e = vnorm(e_vec)
    # Energy -> semi-major axis
    eps = V*V/2 - MU_EARTH/R
    a = -MU_EARTH/(2*eps) if abs(eps) > 1e-12 else float('inf')

    # Inclination
    i = math.degrees(math.acos(h[2]/H))

    # RAAN
    raan = 0.0
    if N > 1e-10:
        raan = math.degrees(math.atan2(n[1], n[0])) % 360.0

    # Argument of perigee
    argp = 0.0
    if N > 1e-10 and e > 1e-10:
        argp = math.degrees(math.atan2(vdot(vxs(n, e_vec), h)/H, vdot(n, e_vec)/N)) % 360.0

    # True anomaly
    nu = 0.0
    if e > 1e-10:
        nu = math.degrees(math.atan2(vdot(vxs(e_vec, r), h)/H, vdot(e_vec, r)/e)) % 360.0
    else:
        # circular: use argument of latitude
        u = math.degrees(math.atan2(vdot(vxs(n, r), h)/H, vdot(n, r)/N)) % 360.0
        nu = u  # treat as true anomaly proxy

    return OrbitalElements(a, e, i, raan, argp, nu)

# ---------------------------- Mean motion & anomalies ----------------------------

def kepler_E_from_nu(nu_rad: float, e: float) -> float:
    if e < 1e-8:
        return nu_rad
    return math.atan2(math.sin(nu_rad)*math.sqrt(1 - e*e), e + math.cos(nu_rad))

def mean_from_true(nu_deg: float, e: float) -> float:
    nu = math.radians(nu_deg)
    E = kepler_E_from_nu(nu, e)
    M = E - e*math.sin(E)
    return math.degrees(M)

# ---------------------------- TLE formatting ----------------------------

def _tle_checksum(line_no_cs: str) -> str:
    s = 0
    for ch in line_no_cs:
        if ch.isdigit():
            s += int(ch)
        elif ch == '-':
            s += 1
    return str(s % 10)


def _epoch_tle(dt: datetime) -> str:
    # TLE epoch: YYDDD.dddddddd (UTC)
    year = dt.year % 100
    doy = (dt - datetime(dt.year, 1, 1, tzinfo=timezone.utc)).total_seconds()/86400.0 + 1
    return f"{year:02d}{doy:012.8f}"  # includes leading zeros


def build_tle(coe: OrbitalElements, epoch_utc: datetime,
              satnum: int = 99999, classification: str = 'U',
              intldesg: str = '25001A', revnum: int = 1,
              bstar: float = 0.0, mean_motion_rev_per_day: float | None = None,
              force_circular_if_mapping: bool = False) -> Tuple[str,str]:
    i = coe.i_deg
    raan = coe.raan_deg
    e = max(0.0, min(0.9999999, coe.e))
    argp = coe.argp_deg
    M = mean_from_true(coe.nu_deg, e)

    if mean_motion_rev_per_day is None:
        # Compute from a
        n_rad_s = math.sqrt(MU_EARTH/(coe.a_km**3))
        mean_motion_rev_per_day = n_rad_s * 86400.0 / (2*math.pi)

    # Eccentricity in TLE has no decimal point: 7 digits
    e_7 = f"{int(round(e*1e7)):07d}"

    # B* scientific notation in TLE format (symmetric mantissa exponent 5 digits)
    def bstar_tle(b):
        if b == 0.0:
            return " 00000-0"
        expo = 0
        mant = abs(b)
        while mant >= 1.0:
            mant /= 10.0
            expo += 1
        while mant < 0.1:
            mant *= 10.0
            expo -= 1
        sgn = '-' if b < 0 else ' '
        return f"{sgn}{mant:5.5f}{expo:+d}".replace('+', '')

    epoch = _epoch_tle(epoch_utc)

    line1_core = (
        f"1 {satnum:05d}{classification} {intldesg:>8} {epoch} "
        f".00000000  00000-0 {bstar_tle(bstar)} 0  999"
    )
    line1 = line1_core + _tle_checksum(line1_core)

    line2_core = (
        f"2 {satnum:05d} "
        f"{i:8.4f} "
        f"{raan:8.4f} "
        f"{e_7} "
        f"{argp:8.4f} "
        f"{M:8.4f} "
        f"{mean_motion_rev_per_day:11.8f}{revnum:5d}"
    )
    line2 = line2_core + _tle_checksum(line2_core)
    return line1, line2

# ---------------------------- Main entry ----------------------------

def generate_tle_from_waypoints(
    waypoints: Iterable[Tuple[float,float,float,str]],
    sensor_lat_deg: float = 42.6977,  # Sofia
    sensor_lon_deg: float = 23.3219,
    sensor_alt_m: float = 550.0,
    map_to_space: bool = False,
    target_alt_km: float = 500.0,
    small_e: float = 0.001
) -> Tuple[str,str,OrbitalElements]:
    """
    waypoints: iterable of (range_m, az_deg, el_deg, timestamp_iso8601_utc)
    Returns: (TLE line1, TLE line2, OrbitalElements_used)
    """
    wps = list(waypoints)
    if len(wps) < 3:
        raise ValueError("Need at least 3 waypoints for Herrick–Gibbs")

    # Convert to ECEF then to ECI for each waypoint
    site_ecef = geodetic_to_ecef(sensor_lat_deg, sensor_lon_deg, sensor_alt_m)
    Renu2ecef = enu_to_ecef_matrix(sensor_lat_deg, sensor_lon_deg)

    def enu_to_ecef(enu):
        e = Renu2ecef[0][0]*enu[0] + Renu2ecef[0][1]*enu[1] + Renu2ecef[0][2]*enu[2]
        n = Renu2ecef[1][0]*enu[0] + Renu2ecef[1][1]*enu[1] + Renu2ecef[1][2]*enu[2]
        u = Renu2ecef[2][0]*enu[0] + Renu2ecef[2][1]*enu[1] + Renu2ecef[2][2]*enu[2]
        return (site_ecef[0]+e, site_ecef[1]+n, site_ecef[2]+u)

    eci_positions_km: List[Tuple[float,float,float]] = []
    times_utc: List[datetime] = []

    for Rm, az, el, ts in wps:
        enu = spherical_local_to_enu(Rm, az, el)
        ecef = enu_to_ecef(enu)
        dt = _to_datetime_utc(ts)
        eci_m = ecef_to_eci(ecef, dt)
        eci_km = (eci_m[0]/1000.0, eci_m[1]/1000.0, eci_m[2]/1000.0)
        eci_positions_km.append(eci_km)
        times_utc.append(dt)

    # Use the middle 3 (first, middle, last) for HG; if >3 points, pick 3 spread out
    idx1 = 0
    idx3 = len(wps) - 1
    idx2 = (idx1 + idx3)//2

    r1 = eci_positions_km[idx1]
    r2 = eci_positions_km[idx2]
    r3 = eci_positions_km[idx3]

    t1 = (times_utc[idx1] - times_utc[0]).total_seconds()
    t2 = (times_utc[idx2] - times_utc[0]).total_seconds()
    t3 = (times_utc[idx3] - times_utc[0]).total_seconds()

    # Herrick–Gibbs for v2
    v2_km_s = herrick_gibbs(r1, r2, r3, t1, t2, t3)

    # COEs from (r2, v2)
    coe = rv_to_coe(r2, v2_km_s)

    # Mapping option: keep plane, set a to target radius
    if map_to_space:
        a_target = R_EARTH_KM + target_alt_km
        # keep plane (i, raan), keep argp, set small eccentricity
        coe = OrbitalElements(
            a_km=a_target,
            e=max(1e-6, small_e),
            i_deg=coe.i_deg,
            raan_deg=coe.raan_deg,
            argp_deg=coe.argp_deg,
            nu_deg=coe.nu_deg,
        )

    # Epoch = time of middle point
    epoch = times_utc[idx2]

    # Build TLE (rev/day from a)
    line1, line2 = build_tle(coe, epoch)
    return line1, line2, coe

# ---------------------------- Example usage ----------------------------
if __name__ == "__main__":
    # Example with dummy data (replace with your actual logs)
    sofia_lat, sofia_lon, sofia_alt = 42.6977, 23.3219, 550.0
    waypoints = [
        # (range_m, az_deg, el_deg, ISO8601_UTC)
        (1000.0, 0.0, 45.0,  "2025-08-14T12:00:00.000Z"),
        (1005.0, 10.0, 46.0, "2025-08-14T12:00:01.000Z"),
        (1012.0, 20.0, 47.0, "2025-08-14T12:00:02.000Z"),
    ]

    tle1, tle2, coe = generate_tle_from_waypoints(
        waypoints,
        sensor_lat_deg=sofia_lat,
        sensor_lon_deg=sofia_lon,
        sensor_alt_m=sofia_alt,
        map_to_space=True,       # toggle here
        target_alt_km=500.0,
    )

    print(tle1)
    print(tle2)
    print(coe)