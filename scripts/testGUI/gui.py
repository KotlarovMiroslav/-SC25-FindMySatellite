import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (needed for 3D plot)

# --- Configurable settings ---
north_direction = np.array([0, 1, 0])  # "North" is along +Y axis
north_length = 200
num_generated_points = 20  # Number of fake scan points

# --- Point generator ---
def generate_points(n=10, radius=500):
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
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# Origin (red dot)
ax.scatter(0, 0, 0, c='red', s=50, label='Origin')

# North direction (green line)
north_end = north_direction / np.linalg.norm(north_direction) * north_length
ax.plot([0, north_end[0]], [0, north_end[1]], [0, north_end[2]], c='green', label='North')

# Generated scan points (blue)
# scan_points = generate_points(num_generated_points, radius=500)
# ax.scatter(scan_points[:, 0], scan_points[:, 1], scan_points[:, 2],
#            c='blue', s=20, label='Detected points')

# --- Axes settings ---
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D LiDAR Visualization')
ax.legend()
ax.set_box_aspect([1, 1, 1])  # Equal aspect ratio

lim = 200
ax.set_xlim([-lim, lim])
ax.set_ylim([-lim, lim])
ax.set_zlim([0, lim])

# Create scan line
scan_line, = ax.plot([], [], [], c='red', label='LiDAR direction', linewidth=2)

# --- Marker storage ---
marker_points = {'x': [], 'y': [], 'z': []}
marker_plot = ax.scatter([], [], [], c='blue', s=30)
marked_angles = set()

# Parameters
scan_length = 200
angle_deg = 0

def update(frame):
    global angle_deg, marked_angles

    prev_angle = angle_deg
    angle_deg = (angle_deg + 3) % 360
    angle_rad = np.deg2rad(angle_deg)

    x_end = scan_length * np.cos(angle_rad)
    y_end = scan_length * np.sin(angle_rad)
    z_end = scan_length * np.sin(angle_rad)
    if z_end < 0:
        z_end = -z_end

    if angle_deg < prev_angle:
        marker_points['x'].clear()
        marker_points['y'].clear()
        marker_points['z'].clear()
        marked_angles.clear()

    scan_line.set_data([0, x_end], [0, y_end])
    scan_line.set_3d_properties([0, z_end])

    if int(angle_deg) % 20 == 0 and angle_deg not in marked_angles:
        marker_points['x'].append(x_end)
        marker_points['y'].append(y_end)
        marker_points['z'].append(z_end)
        marked_angles.add(angle_deg)

    # Instead of removing/re-creating:
    coords = np.column_stack([marker_points['x'], marker_points['y']])
    marker_plot._offsets3d = (marker_points['x'], marker_points['y'], marker_points['z'])

    return scan_line, marker_plot


# Run animation
ani = FuncAnimation(fig, update, frames=range(0, 360, 3), interval=50, blit=False)
plt.show()
