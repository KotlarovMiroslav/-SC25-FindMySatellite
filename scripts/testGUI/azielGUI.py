import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import globalValues
from pcServer import communicate_with_pi
import threading
import findVernalPoint
from matplotlib.widgets import Button
from sgp4.api import Satrec, jday
import datetime as dt
import time

time.sleep(2)  # Ensure the server is ready before starting the GUI
def gui():
    north_direction = np.array([0, 1, 0])
    north_length = 200
    vernal_az, vernal_alt = findVernalPoint.findVernalPoint()
    vp_az = np.deg2rad(vernal_az)
    vp_el = np.deg2rad(vernal_alt)

    x_vp = 500 * np.cos(vp_el) * np.sin(vp_az)
    y_vp = 500 * np.cos(vp_el) * np.cos(vp_az)
    z_vp = 500 * np.sin(vp_el)
    vernalPoint_direction = np.array([x_vp, y_vp, z_vp])

    # --- Create figure/axes ---
    fig = plt.figure(figsize=(9, 9))
    ax = fig.add_subplot(111, projection="3d")

    # Origin and reference lines
    ax.scatter(0, 0, 0, c="red", s=50, label="Origin")
    north_end = north_direction / np.linalg.norm(north_direction) * north_length
    ax.plot([0, north_end[0]], [0, north_end[1]], [0, north_end[2]], c="green", label="North")
    vp_end = vernalPoint_direction / np.linalg.norm(vernalPoint_direction) * 500
    ax.plot([0, vp_end[0]], [0, vp_end[1]], [0, vp_end[2]], c="purple", label="Vernal Point")

    # Axes formatting
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("3D LiDAR + TLE Visualization")
    ax.legend()
    ax.set_box_aspect([1, 1, 1])
    lim = 550
    ax.set_xlim([-lim, lim])
    ax.set_ylim([-lim, lim])
    ax.set_zlim([0, lim])

    # --- LiDAR objects ---
    scan_line, = ax.plot([], [], [], c="red", label="LiDAR direction", linewidth=2)
    marker_points = {"x": [], "y": [], "z": []}
    marker_plot = ax.scatter([], [], [], c="blue", s=30)
    marked_angles = set()

    # --- TLE storage ---
    tle_lines = []

    # --- Buttons for TLE ---
    btn_ax = plt.axes([0.1, 0.01, 0.15, 0.05])
    btn_tle = Button(btn_ax, "Load TLE")
    clear_ax = plt.axes([0.3, 0.01, 0.15, 0.05])
    btn_clear = Button(clear_ax, "Clear TLEs")

    def load_tle(event):
        try:
            with open("C:\\xampp\\htdocs\\18122\\Python\\1.PrepClass\\stage\\FindMySatellite_SC25\\scripts\\testGUI\\TLE.txt", "r") as f:  # adjust your path if needed
                lines = f.read().splitlines()
            if len(lines) < 3:
                print("TLE file must have 3 lines (name + 2 lines)")
                return

            name, line1, line2 = lines[0], lines[1], lines[2]
            sat = Satrec.twoline2rv(line1, line2)
            start = dt.datetime.utcnow()

            ts = np.linspace(0, 24*60, 200)  # minutes
            xs, ys, zs = [], [], []
            scale_factor = 400/7000.0
            for minutes in ts:
                current = start + dt.timedelta(minutes=float(minutes))
                jd, fr = jday(current.year, current.month, current.day,
                              current.hour, current.minute, current.second + current.microsecond*1e-6)
                e, r, v = sat.sgp4(jd, fr)
                if e == 0:
                    xs.append(r[0]*scale_factor)
                    ys.append(r[1]*scale_factor)
                    zs.append(r[2]*scale_factor)

            line, = ax.plot(xs, ys, zs, label=name, color="orange")
            tle_lines.append(line)
            ax.legend()
            plt.draw()
        except Exception as e:
            print("Error reading TLE:", e)

    def clear_tles(event):
        for line in tle_lines:
            line.remove()
        tle_lines.clear()
        plt.draw()

    btn_tle.on_clicked(load_tle)
    btn_clear.on_clicked(clear_tles)

    # --- Animation update ---
    def update(frame):
        if globalValues.readyToPlot == 1:
            azimuth_deg = round(globalValues.el,2)
            elevation_deg = round(globalValues.az,2)
            az_rad = np.deg2rad(azimuth_deg)
            el_rad = np.deg2rad(elevation_deg)

            x_end = globalValues.scanLength * np.cos(el_rad) * np.cos(az_rad)
            y_end = globalValues.scanLength * np.cos(el_rad) * np.sin(az_rad)
            z_end = abs(globalValues.scanLength * np.sin(el_rad))
            # print(f"x_end{x_end}, y_end{y_end}, z_end{z_end}")
            scan_line.set_data([0, x_end], [0, y_end])
            scan_line.set_3d_properties([0, z_end])

            if globalValues.mark == 1:
                globalValues.mark = 0  # Reset readyToPlot after processing
                marker_points["x"].append(x_end)
                marker_points["y"].append(y_end)
                marker_points["z"].append(z_end)
                marked_angles.add(azimuth_deg)
                marker_plot._offsets3d = (marker_points["x"], marker_points["y"], marker_points["z"])

        return scan_line, marker_plot

    ani = FuncAnimation(fig, update, frames=range(0, 360, 1), interval=10, blit=False)
    plt.show()


# --- Start comms thread + run GUI ---
t_coms = threading.Thread(target=communicate_with_pi, daemon=True)
t_coms.start()
gui()
