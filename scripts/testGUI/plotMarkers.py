import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# Limits
lim = 20
ax.set_xlim([-lim, lim])
ax.set_ylim([-lim, lim])
ax.set_zlim([0, lim/2])  # Keep flat

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_box_aspect([1, 1, 0.5])

# Origin
ax.scatter(0, 0, 0, c='red', s=50)

# Scan line
scan_line, = ax.plot([], [], [], c='red', linewidth=2)

# Store markers
marker_points = {'x': [], 'y': [], 'z': []}
marker_plot = ax.scatter([], [], [], c='blue', s=30)

# Parameters
scan_length = 18
angle_deg = 0
marked_angles = set()

def update(frame):
    global angle_deg, marker_points, marker_plot, marked_angles
    prev_angle = angle_deg
    angle_deg = (angle_deg + 3) % 360
    angle_rad = np.deg2rad(angle_deg)

    # End point
    x_end = scan_length * np.cos(angle_rad)
    y_end = scan_length * np.sin(angle_rad)
    z_end = scan_length * np.sin(angle_rad)
    if z_end < -1:
        z_end = z_end * -1

    # Reset markers at start of a new sweep
    if angle_deg < prev_angle:
        marker_points = {'x': [], 'y': [], 'z': []}
        marked_angles.clear()

    # Update scan line
    scan_line.set_data([0, x_end], [0, y_end])
    scan_line.set_3d_properties([0, z_end])

    # Place marker every 10 degrees (only once per angle per sweep)
    if int(angle_deg) % 2 == 0 and angle_deg not in marked_angles:
        marker_points['x'].append(x_end)
        marker_points['y'].append(y_end)
        marker_points['z'].append(z_end)
        marked_angles.add(angle_deg)

    # Update markers
    marker_plot.remove()
    marker_plot = ax.scatter(marker_points['x'], marker_points['y'], marker_points['z'],
                             c='blue', s=25)

    return scan_line, marker_plot

ani = FuncAnimation(fig, update, frames=range(0, 360, 3), interval=50, blit=False)
plt.show()
