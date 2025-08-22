# Demo File to create TLE from waypoints
import numpy as np
import create_tle as tc
import sys
import os
import globalsConfig as gv


# get the parent directory of utils
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


# Demo waypoints (azimuth, elevation, range, time)
'''
waypoints = np.array([
    [0,     90,    180],  # azimuth degrees
    [0,     45,    0],  # elevation degrees
    [100,   100,   100],  # distance in cm
    [5,     10,    15]  # time in ms
])
'''

def gen_tle():

    waypoints = np.array([
        [gv.det_pos[2][0], gv.det_pos[4][0],gv.det_pos[6][0]],
        [gv.det_pos[2][1], gv.det_pos[4][1],gv.det_pos[6][1]],
        [gv.det_pos[2][2], gv.det_pos[4][2],gv.det_pos[6][2]],
        [gv.det_pos[2][3], gv.det_pos[4][3],gv.det_pos[6][3]],
    ])


    # Create TLE
    line1, line2 = tc.calcTLE(waypoints)

    with open("pi_tle.txt", "w") as f:
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


