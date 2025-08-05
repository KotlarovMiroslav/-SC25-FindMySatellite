import numpy as np

G = 6.67430e-20
M_EARTH = 5.972e24

def acceleration_gravity(pos, G, M):
    r = np.linalg.norm(pos) # norm is just manfitude of the position vector
    return -G * M * pos / r**3

def Kepler_Verlet(pos0, vel0, t_params, G=G, M=M_EARTH):

    # t_arr: Time array [s]
    # pos_arr: Array of position vectors [N x 3] [km]
    # vel_arr: Array of velocity vectors [N x 3] [km/s]

    t0, tf, N = t_params
    dt = (tf - t0) / (N - 1)

    t_arr = np.linspace(t0, tf, N)
    
    # initialise the arrays
    pos_arr = np.zeros((N, 3))
    vel_arr = np.zeros((N, 3))

    pos_arr[0] = pos0
    vel_arr[0] = vel0
    acc = acceleration_gravity(pos0, G, M)

    for i in range(1, N):
        pos_arr[i] = pos_arr[i-1] + vel_arr[i-1] * dt + 0.5 * acc * dt**2
        new_acc = acceleration_gravity(pos_arr[i], G, M)
        vel_arr[i] = vel_arr[i-1] + 0.5 * (acc + new_acc) * dt
        acc = new_acc

    return t_arr, pos_arr, vel_arr
