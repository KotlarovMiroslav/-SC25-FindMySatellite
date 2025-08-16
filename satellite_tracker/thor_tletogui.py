from sgp4.api import jday
import math

def satrec_to_valid_tle(satrec):
    """
    Convert a Satrec object to a valid, propagator-ready TLE string.
    """

    # Epoch conversion
    year = satrec.epochyr
    if year < 57:
        year += 2000
    else:
        year += 1900

    # Convert epochdays to day-of-year + fraction
    day_of_year = int(satrec.epochdays)
    fraction_of_day = satrec.epochdays - day_of_year
    hh = int(fraction_of_day * 24)
    mm = int((fraction_of_day*24 - hh)*60)
    ss = ((fraction_of_day*24 - hh)*60 - mm)*60
    fractional_day = day_of_year + (hh + mm/60 + ss/3600)/24

    # Line 1
    line1 = (
        f"1 {satrec.satnum:05d}U {satrec.launch:03d} "
        f"{str(satrec.epochyr).zfill(2)}{satrec.epochdays:012.8f} "
        f"{satrec.ndot: .8f} {satrec.nddot: .8f} {satrec.bstar: .8f} "
        f"{satrec.elnum:4d}"
    )
    checksum1 = sum((int(c) if c.isdigit() else 1 if c == '-' else 0) for c in line1[:68]) % 10
    line1 = f"{line1[:68]}{checksum1}"

    # Line 2
    incl = satrec.inclo * 180.0 / math.pi
    raan = satrec.nodeo * 180.0 / math.pi
    argp = satrec.argpo * 180.0 / math.pi
    mean_anomaly = satrec.mo * 180.0 / math.pi
    mean_motion = satrec.no_kozai * 1440.0 / (2*math.pi)  # rev/day
    ecco = int(round(satrec.ecco * 1e7))

    line2 = (
        f"2 {satrec.satnum:05d} "
        f"{incl:8.4f} {raan:8.4f} {ecco:07d} "
        f"{argp:8.4f} {mean_anomaly:8.4f} {mean_motion:11.8f}"
    )
    checksum2 = sum((int(c) if c.isdigit() else 1 if c == '-' else 0) for c in line2[:68]) % 10
    line2 = f"{line2[:68]}{checksum2}"

    return line1 + "\n" + line2

# Example usage
from sgp4.api import Satrec, WGS72

satellite = Satrec()
satellite.sgp4init(
    WGS72, 'i', 12345, 0, 0.0, 0.0, 0.0, 0.0,
    51.6, 0.0, 0.001, 0.0, 0.0, 15.0
)

tle = satrec_to_valid_tle(satellite)
print(tle)