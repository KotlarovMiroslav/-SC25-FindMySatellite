from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u

def findVernalPoint():
    """
    This function calculates the Vernal Point in AltAz coordinates for a given location and time.
    The Vernal Point is the point in the sky where the Sun crosses the celestial equator moving northward.
    """
    # Define the Vernal Point in ICRS coordinates
    vernal_point = SkyCoord(ra=0*u.hourangle, dec=0*u.deg, frame="icrs")
    
    # Location: Sofia, Bulgaria
    sofia = EarthLocation(lat=42.7*u.deg, lon=23.3*u.deg, height=0*u.m)
    
    # Current time
    now = Time.now()
    
    # AltAz transformation
    altaz_frame = AltAz(obstime=now, location=sofia)
    vernal_altaz = vernal_point.transform_to(altaz_frame)
    
    return vernal_altaz.alt.deg, vernal_altaz.az.deg



# # Define the Vernal Point in ICRS coordinates
# vernal_point = SkyCoord(ra=0*u.hourangle, dec=0*u.deg, frame="icrs")

# # Location: Sofia, Bulgaria
# sofia = EarthLocation(lat=42.7*u.deg, lon=23.3*u.deg, height=0*u.m)

# # Current time
# now = Time.now()

# # AltAz transformation
# altaz_frame = AltAz(obstime=now, location=sofia)
# vernal_altaz = vernal_point.transform_to(altaz_frame)

# print("Altitude:", vernal_altaz.alt.deg, "deg")
# print("Azimuth (from North):", vernal_altaz.az.deg, "deg")
