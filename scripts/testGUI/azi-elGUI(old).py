import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (needed for 3D plot)
import globalValues
from pcServer import communicate_with_pi
import threading
import findVernalPoint

# --- Configurable settings ---
def gui():
    north_direction = np.array([0, 1, 0])  # "North" is along +Y axis
    north_length = 200
    vernal_az, vernal_alt = findVernalPoint.findVernalPoint()
    print(vernal_az)
    print(vernal_alt)
    vp_az = np.deg2rad(vernal_az)
    vp_el = np.deg2rad(vernal_alt)

    x_vp = 500 * np.cos(vp_el) * np.sin(vp_az)
    y_vp = 500 * np.cos(vp_el) * np.cos(vp_az)
    z_vp = 500 * np.sin(vp_el)
    vernalPoint_direction = np.array([x_vp, y_vp, z_vp])
    print (f"Vernal Point Direction: {vernalPoint_direction}")
    
    
    # --- Point generator ---
    # def generate_points(n=10, radius=500):
    #     points = []
    #     for _ in range(n):
    #         theta = np.random.uniform(0, 2*np.pi)
    #         phi = np.random.uniform(0, np.pi)
    #         r = np.random.uniform(0, radius)
    #         x = r * np.sin(phi) * np.cos(theta)
    #         y = r * np.sin(phi) * np.sin(theta)
    #         z = r * np.cos(phi)
    #         points.append([x, y, z])
    #     return np.array(points)

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
    vp_end = vernalPoint_direction / np.linalg.norm(vernalPoint_direction) * 500
    ax.plot([0, vp_end[0]], [0, vp_end[1]], [0, vp_end[2]], c='purple', label='Vernal Point')
    # --- Axes settings ---
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D LiDAR Visualization')
    ax.legend()
    ax.set_box_aspect([1, 1, 1])  # Equal aspect ratio

    lim = 550
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
    scan_length = 550
    angle_deg = 0
    azimuth_deg = 0
    elevation_deg = 0

    def update(frame):
        #readyToPlot,az,el,scanLength 
        # print(f"az{az},el{el},scanLength{scanLength}")
        if globalValues.readyToPlot == 1:
            # i = frame % len(azimuthArr)
            # if i >= len(azimuthArr):
            #     i = 0
            global azimuth_deg,elevation_deg
            azimuth_deg = globalValues.az #  put value stepper motor angle here
            elevation_deg = globalValues.el #put value for servo angle here
            az_rad = np.deg2rad(azimuth_deg) #np.deg2rad(azimuth_deg)
            el_rad = np.deg2rad(elevation_deg) #np.deg2rad(elevation_deg)
            

            x_end = globalValues.scanLength * np.cos(el_rad) * np.cos(az_rad)
            y_end = globalValues.scanLength * np.cos(el_rad) * np.sin(az_rad)
            z_end = globalValues.scanLength * np.sin(el_rad) #globalValues.scanLength * np.sin(el_rad)
            print(f"x_end{x_end}, y_end{y_end}, z_end{z_end}")
            '''if z_end < 0:
                z_end = -z_end'''


            scan_line.set_data([0, x_end], [0, y_end])
            scan_line.set_3d_properties([0, z_end])

            if int(azimuth_deg) % 2 == 0 and azimuth_deg not in marked_angles:#Check if global boolean for scanned object is 1 
                marker_points['x'].append(x_end)
                marker_points['y'].append(y_end)
                marker_points['z'].append(z_end)
                marked_angles.add(azimuth_deg)
                marker_plot._offsets3d = (marker_points['x'], marker_points['y'], marker_points['z'])
            

        
        return scan_line, marker_plot


    # Run animation
    ani = FuncAnimation(fig, update, frames=range(0, 360, 3), interval=50, blit=False)
    plt.show()


t_coms = threading.Thread(target=communicate_with_pi, daemon=True)
t_coms.start()
gui()
