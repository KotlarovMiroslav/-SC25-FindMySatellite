import numpy as np

# Function to take in at least 3 waypoints and create a TLE out of it

POINT_NUMBER = 3
TIMESTEP_NUMBER = 2

# Function to read the array with the waypoints
# Input: 
#   waypoint[0,:] is the azimuth, the turn of the stepper
#   waypoint[1,:] is the elevation, the inclination of the servo
#   waypoint[2,:] is the range, distance from the station (lidar reading)
#   waypoint[3,:] is the time after starting the readings
#   angles are in degrees
#   time is time since start, not yet the needed timestep between each point

def read_points(waypoints):
    azimuth = waypoints[0, :]
    elevation = waypoints[1, :]
    range = waypoints[2, :]
    time = waypoints[3, :]

    # convert azimuth of stepper to take north as zero (-90 degrees)
    phi = azimuth - 90
    phi_rad = np.radians(phi)  # Convert to radians

    # convert elevation of servo to take zenith as zero (90 degrees - theta)
    theta = 90 - elevation
    theta_rad = np.radians(theta)  # Convert to radians

    return phi_rad, theta_rad, range, time


# each time step is the difference between consecutive time readings
# needed for the difference in time of the velocity vector
# naming convention -> first time step is between first reading and second reading

def calculateTimestep(time):
    timestep = np.zeros(len(time) - 1)
    for i in range(len(timestep)):
        timestep[i] = time[i + 1] - time[i]
    return timestep

# convert given coordinate system (ECI) from a sperical one to cartesian

def convertKOS(phi_rad, theta_rad, range):
    x = range * np.sin(theta_rad) * np.cos(phi_rad)
    y = range * np.sin(theta_rad) * np.sin(phi_rad)
    z = range * np.cos(theta_rad)

    point_vector = np.array([x, y, z])
    return x, y, z

# calculate the velocity at the middle of the three used points

def calcVelocity(point_vector, timestep):
    if len(point_vector) != POINT_NUMBER or len(timestep) != TIMESTEP_NUMBER:
        raise ValueError("Invalid input shapes")

    # Calculate the velocity vector as the difference between the last two points
    velocity = (point_vector[2] - point_vector[0]) / timestep[0]
    return velocity

# calculate the angular Momentum 

def calcAngularMomentum(point_vector, velocity):
    if len(point_vector) != POINT_NUMBER or len(velocity) != POINT_NUMBER:
        raise ValueError("Invalid input shapes")

    # Calculate the angular momentum vector
    angular_momentum = np.cross(point_vector, velocity)
    return angular_momentum

# calculate the inclination of the trajectory

def calcInclination(point_vector):
    if len(point_vector) != POINT_NUMBER:
        raise ValueError("Invalid input shapes")
