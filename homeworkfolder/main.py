from Integrators import Verlet_3D
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

if __name__ == "__main__":
    # Circular orbit setup
    pos_0 = [7000.0, 0.0, 0.0]   # [km]
    vel_0 = [0.0, 7.546, 0.0]    # [km/s] — circular velocity at 7000 km

    sim_param = [0.0, 6000.0, 10000]  # [start, stop, steps]
    body_param = [1.0, 0.0]  # unused here, kept for compatibility

    time, pos, vel = Verlet_3D(pos_0, vel_0, body_param, sim_param)

    # Plot in 3D
    x, y, z = pos[:, 0], pos[:, 1], pos[:, 2]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x, y, z, label='Orbit Path')
    ax.set_xlabel("X [km]")
    ax.set_ylabel("Y [km]")
    ax.set_zlabel("Z [km]")
    ax.set_title("3D Orbit Trajectory")
    ax.legend()
    plt.grid(True)
    plt.show()
