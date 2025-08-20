import numpy as np
from sgp4.api import Satrec, jday, WGS72
from sgp4 import exporter
import math

# Function to take in at least 3 waypoints and create a TLE out of it

POINT_NUMBER = 3
TIMESTEP_NUMBER = 2
MU_EARTH = 398600.4418  # km^3/s^2, standard gravitational parameter
R_EARTH = 6378.137      # km, mean Earth radius
TIME_SCALING = 200

#  z-axis unit vector k vector
k = np.array([0, 0, 1])

# Function to read the array with the waypoints
# Input: 
#   waypoint[0,:] is the azimuth, the turn of the stepper
#   waypoint[1,:] is the elevation, the inclination of the servo
#   waypoint[2,:] is the range, distance from the station (lidar reading)
#   waypoint[3,:] is the time after starting the readings
#   angles are in degrees
#   time is time since start, not yet the needed timestep between each point
# Output: phi and theta in rad, distance in km and time in s

def read_points(waypoints):
    azimuth = waypoints[0, :]
    elevation = waypoints[1, :]
    distance_cm = waypoints[2, :]
    time = waypoints[3, :]/1000             # make seconds out of the ms 

    # convert azimuth of stepper to take north as zero (-90 degrees)
    phi = azimuth - 90
    phi_rad = np.radians(phi)               # Convert to radians

    # convert elevation of servo to take zenith as zero (90 degrees - elevation)
    theta = 90 - elevation
    theta_rad = np.radians(theta)           # Convert to radians

    # convert distance to kilometers instead of cm
    distance_km = (distance_cm/(100*1000))
    # add the earth radius and scale it to a rough LEO orbit (~500km)
    distance_sat = R_EARTH + distance_km + 499.8

    return phi_rad, theta_rad, distance_sat, time

# each time step is the difference between consecutive time readings
# needed for the difference in time of the velocity vector
# naming convention -> first time step is between first reading and second reading
# Output: Timestep in seconds
# CHANGE: I adjusted a scaling Factor, to get the velocity more real

def calculateTimestep(time):

    timestep = np.zeros(len(time) - 1)
    for i in range(len(timestep)):
        timestep[i] = time[i + 1] - time[i]
        timestep[i] = timestep[i] * TIME_SCALING
    return timestep

# convert given coordinate system (ECI) from a sperical one to cartesian
# Output: Array of three waypoints with x,y,z each x = [0,:], y = [1,:], z = [2,:]

def convertKOS(phi_rad, theta_rad, distance):
    print(distance)
    x = distance * np.sin(theta_rad) * np.cos(phi_rad)
    y = distance * np.sin(theta_rad) * np.sin(phi_rad)
    z = distance * np.cos(theta_rad)

    point_vector = np.array([x, y, z])
    return point_vector

# calculate the velocity at the middle of the three used points
# Output: velocity in kilometers per second

def calcVelocity(point_vector, timestep):

    # use first and last coordinate pointvector [:, 2] -[:,0] 
    #vel = (point_vector[:,2] - point_vector[:,0]) / timestep[0]

    # use first and last coordinate pointvector [:, 2] -[:,0] 
    #vel = (point_vector[:,2] - point_vector[:,0]) / (timestep[0] + timestep[1])

    dist1 = point_vector[:,1] - point_vector[:,0]
    dist2 = point_vector[:,2] - point_vector[:,1]
    total_distance = dist1 + dist2
    total_time = timestep[0] + timestep[1]
    vel = total_distance / total_time

    return vel

# calculate the angular Momentum 
# Output: angular momentum oin ??? unit
def calcAngularMomentum(point_vector, velocity):

    am = np.cross(point_vector[:,1], velocity)
    return am

# calculate the inclination of the trajectory
# Output: Inclination in radians

def calcInclination(angular_momentum):
  
    inc  = np.arccos(angular_momentum[2] / np.linalg.norm(angular_momentum))
    return inc

# calculate the eccentricity of the orbit

def calcEccentricity(point_vector, velocity, angular_momentum):

    r = np.linalg.norm(point_vector[:,1])

    eccentricity_vector = np.cross(velocity,angular_momentum) / MU_EARTH - (point_vector[:,1] / r)
    ecc= np.linalg.norm(eccentricity_vector)
    
    return ecc, eccentricity_vector

# calculate the semi-major axis of the orbit

def calcSemiMajorAxis(point_vector, velocity):

    r = np.linalg.norm(point_vector[:,1])
    v = np.linalg.norm(velocity)

    #  equation: a = μ / (2μ/r - v²)
    sma = MU_EARTH / (2 * MU_EARTH / r - v**2)

    return sma

# calculate RAAN (right ascension of ascending node)
# output size

def calcRAAN(angular_momentum):

    k = np.array([0, 0, 1])
    n = np.cross(k, angular_momentum)
    raan = np.arctan2(n[1], n[0])

    return raan

# calculate argument of periapsis

def calcArgumentOfPeriapsis(eccentricity_vector, angular_momentum):
    k = np.array([0, 0, 1])
    n = np.cross(k, angular_momentum)

    n_cross_e = np.cross(n, eccentricity_vector)               # n x e
    n_cross_e_mag = np.linalg.norm(n_cross_e)     # |n x e|
    n_dot_e = np.dot(n, eccentricity_vector)                   # n · e

    aop = np.arctan2(n_cross_e_mag, n_dot_e)

    return aop

# calculate true anomaly

def calcTrueAnomaly(point_vector, eccentricity_vector):

    ecc_cross_p = np.cross(eccentricity_vector, point_vector[:,1])
    ecc_cross_p_mag = np.linalg.norm(ecc_cross_p)
    ecc_dot_p = np.dot(eccentricity_vector, point_vector[:,1])
    ta = np.arctan2(ecc_cross_p_mag, ecc_dot_p)

    return ta

# calculate mean motion - for now only circular orbit

def calcMeanMotion(sma):
    # sma is radius
    n_rad_s = math.sqrt(MU_EARTH / (sma**3))   # rad/s
    n_rev_day = n_rad_s * 86400 / (2 * math.pi)  # rev/day
    mm = n_rev_day * 2 * math.pi / 1440.0  # radians per minute
    return mm

def calcTLE(waypoints):
 
    phi_rad, theta_rad, distance, time = read_points(waypoints)
    print(f"phi_rad: {phi_rad}, theta_rad: {theta_rad}, distance: {distance}, time: {time}")

    timestep = calculateTimestep(time)
    print(f"Timestep: {timestep}")

    point_vector = convertKOS(phi_rad, theta_rad, distance)
    print(f"Point Vector: {point_vector}")
    
    velocity = calcVelocity(point_vector, timestep)
    print(f"Velocity: {velocity}")

    angular_momentum = calcAngularMomentum(point_vector, velocity)
    print(f"Angular Momentum: {angular_momentum}")

    # Keplerian Elements 
    
    # For a round orbit without inclination inc = 0
    #inclination = 0
    inclination = calcInclination(angular_momentum)
    print(f"Inclination: {inclination}")

    # For a circular orbit eccentricity = 0
    eccentricity = 0
    eccentricity_vector = [0,0,0]
    #eccentricity, eccentricity_vector = calcEccentricity(point_vector, velocity, angular_momentum)
    print(f"Eccentricity: {eccentricity}")
    print(f"Eccentricity Vector: {eccentricity_vector}")

    # For a circular orbit this is the radius
    sma = distance[1]
    #sma = calcSemiMajorAxis(point_vector, velocity)
    print(f"Semi-Major Axis: {sma}")

    raan = calcRAAN(angular_momentum)
    raan = raan % (2 * math.pi) # wrap incase of negative angle
    print(f"RAAN: {raan}")

    # AOP: This quantity is undefined for circular orbits, but is often set to zero instead by convention
    aop = 0
    #aop = calcArgumentOfPeriapsis(eccentricity_vector, angular_momentum)
    print(f"Argument of Periapsis: {aop}")

    ta = calcTrueAnomaly(point_vector, eccentricity_vector)
    print(f"True Anomaly: {ta}")

    mm = calcMeanMotion(sma)
    print(f"Mean Motion: {mm}")

    #https://rhodesmill.org/skyfield/earth-satellites.html#generating-a-satellite-position

    foundmysatellite = Satrec()
    foundmysatellite.sgp4init(
        WGS72,           # gravity model
        'i',             # 'a' = old AFSPC mode, 'i' = improved mode
        69420,           # satnum: Satellite number
        27626.2997,      # epoch: days since 1949 December 31 00:00 UT
        0.0,             # bstar: drag coefficient (/earth radii)
        0.0,             # ndot: ballistic coefficient (radians/minute^2)
        0.0,             # nddot: second derivative of mean motion (radians/minute^3)
        eccentricity,    # ecco: eccentricity
        aop,             # argpo: argument of perigee (radians)
        inclination,     # inclo: inclination (radians)
        ta,              # mo: mean anomaly (radians) -> only for circular orbit true anomaly = mean anomaly
        mm,              # no_kozai: mean motion (radians/minute)
        raan,            # nodeo: right ascension of ascending node (radians)
    )

    line1, line2 = exporter.export_tle(foundmysatellite)

    return line1, line2

