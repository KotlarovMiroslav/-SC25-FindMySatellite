import numpy as np
import csv
import matplotlib.pyplot as plt
from VerletIntegrator import Kepler_Verlet  

# --------------------------------------------------
# Function to parse STK/GMAT output CSV file
# --------------------------------------------------
def parse_orbit_data(filename):
    with open(filename, "r") as fp:
        data = list(csv.reader(fp))

    header = data[0]
    rows = data[1:]  # Skip header

    n = len(rows)
    time = np.zeros(n)
    pos = np.zeros((3, n))
    vel = np.zeros((3, n))

    for i, row in enumerate(rows):
        time[i] = float(row[0])
        pos[:, i] = list(map(float, row[1:4]))
        vel[:, i] = list(map(float, row[4:7]))

    return time, pos, vel

# --------------------------------------------------
# Main Script
# --------------------------------------------------
if __name__ == "__main__":
    # Load STK/GMAT data
    file_name = "Satellite_PVT_GMAT.csv"
    time, pos, vel = parse_orbit_data(file_name)

    # Set initial conditions for integration
    pos_0 = pos[:, 0]
    vel_0 = vel[:, 0]
    t_params = [time[0], time[-1], len(time)]

    # Run Verlet integration
    t_verlet, pos_verlet, vel_verlet = Kepler_Verlet(pos_0, vel_0, t_params)

    # --------------------------------------------------
    # Plot 3D Orbit Comparison
    # --------------------------------------------------
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.plot3D(pos[0], pos[1], pos[2], "green", label="STK")
    ax.plot3D(pos_verlet[:, 0], pos_verlet[:, 1], pos_verlet[:, 2], "red", label="Verlet")
    ax.set_title("3D Orbit Comparison")
    ax.set_xlabel("X [km]")
    ax.set_ylabel("Y [km]")
    ax.set_zlabel("Z [km]")
    ax.legend()
    plt.show()

    # --------------------------------------------------
    # Plot Position Components Over Time
    # --------------------------------------------------
    fig, ax = plt.subplots()
    ax.plot(time, pos[0], "g--", label="X STK")
    ax.plot(time, pos[1], "r--", label="Y STK")
    ax.plot(time, pos[2], "b--", label="Z STK")
    ax.plot(t_verlet, pos_verlet[:, 0], "g", label="X Verlet")
    ax.plot(t_verlet, pos_verlet[:, 1], "r", label="Y Verlet")
    ax.plot(t_verlet, pos_verlet[:, 2], "b", label="Z Verlet")
    ax.set_title("Position Comparison: STK vs Verlet")
    ax.set_xlabel("Time [sec]")
    ax.set_ylabel("Position [km]")
    ax.legend()
    ax.grid(True)
    plt.show()

    # --------------------------------------------------
    # Compute and Plot Position Error
    # --------------------------------------------------
    pos_error = np.linalg.norm(pos_verlet.T - pos, axis=0)

    fig, ax = plt.subplots()
    ax.plot(time, pos_error, color="purple", label="Position Error [km]")
    ax.set_title("Position Error (Verlet vs STK)")
    ax.set_xlabel("Time [sec]")
    ax.set_ylabel("Error [km]")
    ax.legend()
    ax.grid(True)
    plt.show()
