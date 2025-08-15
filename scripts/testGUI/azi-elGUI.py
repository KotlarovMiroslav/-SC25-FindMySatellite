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

azimuthArr = [12.183816906767808, 11.673734659516773, 11.163708187012826, 10.653686783246583, 10.143619743535718, 9.6334563595086, 9.123145915741993, 8.612637687094542, 8.10188093151324, 7.59082489012308, 7.079418779552377, 6.567611791913184, 6.0553530880343365, 5.5425917980741035, 5.029277014101795, 4.515357789447174, 4.000783136968601, 3.4855020236033574, 2.969463370129179, 2.4526160499049823, 1.9349088852722887, 1.4162906476032366, 0.8967100563889645, 0.37611577771221827, 359.8544564241243, 359.331680558989, 358.80773669057766, 358.28257327634867, 357.7561387281265, 357.2283814090701, 356.6992496396376, 356.16869170080224, 355.63665583722326, 355.10309026313234, 354.5679431672296, 354.031162720378, 353.4926970806459, 352.9524944029396, 352.41050284639, 351.866670584694, 351.32094581809974, 350.77327678146037, 350.22361176098883, 349.67189910328705, 349.1180872349686, 348.5621246738764, 348.0039600514072, 347.4435421235696, 346.88081979614435, 346.3157421451103, 345.7482584336596, 345.1783181429258, 344.6058709914465, 344.03086696482455, 343.4532563388192, 342.8729897157973, 342.29001805060403, 341.7042926839466, 341.11576537898384, 340.52438835512515]
elevationArr = [-42.90958461648593, -43.123316381419144, -43.33697881853966, -43.550556212004125, -43.76403285099847, -43.977393024281334, -44.19062101407045, -44.40370108968295, -44.616617503116444, -44.829354481648224, -45.04189622373608, -45.2542268918062, -45.466330607925876, -45.67819144650419, -45.88979343041679, -46.10112052443125, -46.31215662920147, -46.52288557691, -46.73329112489716, -46.94335694985872, -47.153066643143745, -47.36240370472544, -47.57135153773624, -47.779893443428755, -47.988012615755665, -48.19569213438122, -48.40291496198597, -48.60966393772746, -48.815921770614395, -49.02167103635856, -49.22689417094628, -49.431573465574814, -49.63569106188957, -49.839228946475835, -50.04216894605295, -50.24449272193889, -50.446181765867685, -50.647217394436666, -50.84758074478378, -51.047252769555556, -51.24621423169916, -51.44444570112193, -51.641927548627244, -51.83863994312373, -52.0345628455126, -52.22967600609167, -52.42395895855472, -52.6173910184933, -52.809951277530104, -53.00161859972962, -53.19237161974484, -53.38218873694769, -53.5710481140298, -53.758927672850874, -53.945805093142866, -54.13165780757236, -54.31646300099631, -54.500197608017864, -54.682838310333175, -54.86436153575917]
i = 0

def update(frame):
    global i
    if i == len(azimuthArr):
        i = 0
    global angle_deg,marked_angles,azimuth_deg,elevation_deg
    azimuth_deg = azimuthArr[i] # stepper
    elevation_deg = elevationArr[i] #servo
    az_rad = np.deg2rad(azimuth_deg)
    el_rad = np.deg2rad(elevation_deg)
    

    x_end = scan_length * np.cos(el_rad) * np.cos(az_rad)
    y_end = scan_length * np.cos(el_rad) * np.sin(az_rad)
    z_end = scan_length * np.sin(el_rad)

    if z_end < 0:
        z_end = -z_end


    scan_line.set_data([0, x_end], [0, y_end])
    scan_line.set_3d_properties([0, z_end])

    if int(azimuth_deg) % 2 == 0 and azimuth_deg not in marked_angles:#Check if global boolean for scanned object is 1 
        marker_points['x'].append(x_end)
        marker_points['y'].append(y_end)
        marker_points['z'].append(z_end)
        marked_angles.add(azimuth_deg)

    marker_plot._offsets3d = (marker_points['x'], marker_points['y'], marker_points['z'])
    i += 1
    return scan_line, marker_plot


# Run animation
ani = FuncAnimation(fig, update, frames=range(0, 360, 3), interval=50, blit=False)
plt.show()
