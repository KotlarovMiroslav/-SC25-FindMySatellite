import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (needed for 3D plot)
import time

# --- Configurable settings ---
north_direction = np.array([0, 1, 0])  # "North" is along +Y axis for now
north_length = 200                        # How long to draw the north arrow
lidar_direction = np.array([1,0,0])
lidar_length = 200
num_generated_points = 20               # Number of fake scan points

# --- Point generator ---
def generate_points(n=10, radius=500):
    """
    Generate n random points within a sphere of given radius.
    These represent detections from LiDAR.
    """
    points = []
    for _ in range(n):
        theta = np.random.uniform(0, 2*np.pi)
        phi = np.random.uniform(0, np.pi)
        r = np.random.uniform(0, radius)
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        points.append([x, y, z])
    return np.array(points)

# --- Create plot ---
fig = plt.figure(figsize=(200,200))
ax = fig.add_subplot(111, projection='3d')

# Origin (red dot)
ax.scatter(0, 0, 0, c='red', s=50, label='Origin')

# North direction (green line)
north_end = north_direction / np.linalg.norm(north_direction) * north_length
ax.plot([0, north_end[0]],
        [0, north_end[1]],
        [0, north_end[2]],
        c='green', label='North')

# Generated scan points (blue)
scan_points = generate_points(num_generated_points, radius=500)
ax.scatter(scan_points[:, 0], scan_points[:, 1], scan_points[:, 2],
           c='blue', s=20, label='Detected points')

# --- Axes settings ---
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D LiDAR Visualization')
ax.legend()
ax.set_box_aspect([1, 1, 1])  # Equal aspect ratio

# Set axis limits
lim = 200
ax.set_xlim([-lim, lim])
ax.set_ylim([-lim, lim])
ax.set_zlim([0, lim])

# Create an empty line (will be updated in animation)
scan_line, = ax.plot([], [], [], c='red',label='LiDAR direction', linewidth=2)

# Parameters
scan_length = 200
angle_deg = 0

def update(frame):
    global angle_deg
    angle_deg = (angle_deg + 3) % 360  # Rotate clockwise, 3° per frame
    angle_rad = np.deg2rad(angle_deg)
    
    # End point of the scanning line in XY plane
    x_end = scan_length * np.cos(angle_rad)
    y_end = (scan_length * np.sin(angle_rad))
    z_end = scan_length * np.sin(angle_rad)  
    if z_end < 0:
        z_end = z_end * -1
    scan_line.set_data([0, x_end], [0, y_end])
    scan_line.set_3d_properties([0, z_end])
    return scan_line,

# Run animation
ani = FuncAnimation(fig, update, frames=range(0, 360, 3), interval=50, blit=True)

plt.show()




    
