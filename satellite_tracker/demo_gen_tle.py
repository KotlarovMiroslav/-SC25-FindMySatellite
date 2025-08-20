# Demo File to create TLE from waypoints
import numpy as np
import create_tle as tc

# Demo waypoints (azimuth, elevation, range, time)
waypoints = np.array([
    [0,     90,   180],  # azimuth degrees
    [0,     0,    0],  # elevation degrees
    [200,   200,   200],  # distance in cm
    [5000,  10000, 15000]  # time in ms
])

# Create TLE
line1, line2 = tc.calcTLE(waypoints)

with open("tle2.txt", "w") as f:
    f.write("DRONE\n")
    f.write(line1 + "\n")
    f.write(line2 + "\n")

print("tle.txt created successfully!")

# Which Aspects to bullshit: 
    # ecc?
    # setting inclination directly through call value: inc = xyz
    # find it through inclination of middle detection!!!
    # set eccentricity to 0 , since otherwise it calcs more than zero

# use Satrec


