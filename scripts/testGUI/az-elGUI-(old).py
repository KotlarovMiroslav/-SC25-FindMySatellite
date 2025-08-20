import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from sgp4.api import Satrec, jday
import numpy as np
import datetime as dt
import globalValues
import findVernalPoint

def combined_gui():
    fig = plt.figure(figsize=(12, 6))

    # --- Subplot 1: LiDAR ---
    ax1 = fig.add_subplot(121, projection="3d")
    ax1.set_title("3D LiDAR Visualization")

    # Example LiDAR line + scatter
    scan_line, = ax1.plot([], [], [], c="red", linewidth=2)
    marker_plot = ax1.scatter([], [], [], c="blue")

    # --- Subplot 2: TLE Orbit ---
    ax2 = fig.add_subplot(122, projection="3d")
    ax2.set_title("TLE Orbit Drawer")
    ax2.set_xlim([-400, 400])
    ax2.set_ylim([-400, 400])
    ax2.set_zlim([-400, 400])
    tle_lines = []

    # --- Buttons for TLE ---
    btn_ax = plt.axes([0.1, 0.01, 0.15, 0.05])
    btn_tle = Button(btn_ax, "Load TLE")
    clear_ax = plt.axes([0.3, 0.01, 0.15, 0.05])
    btn_clear = Button(clear_ax, "Clear TLEs")

    def load_tle(event):
        try:
            with open("C:\\xampp\\htdocs\\18122\\Python\\1.PrepClass\\stage\\FindMySatellite_SC25\\scripts\\testGUI\\TLE.txt", "r") as f:   # adjust path
                lines = f.read().splitlines()
            if len(lines) < 3:
                return
            name, line1, line2 = lines[0], lines[1], lines[2]
            sat = Satrec.twoline2rv(line1, line2)
            start = dt.datetime.utcnow()

            ts = np.linspace(0, 24*60, 200)
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

            line, = ax2.plot(xs, ys, zs, label=name, color="orange")
            tle_lines.append(line)
            ax2.legend()
            plt.draw()
        except Exception as e:
            print("Error:", e)

    def clear_tles(event):
        for line in tle_lines:
            line.remove()
        tle_lines.clear()
        plt.draw()

    btn_tle.on_clicked(load_tle)
    btn_clear.on_clicked(clear_tles)

    # --- LiDAR animation update ---
    def update(frame):
        if globalValues.readyToPlot == 1:
            az_rad = np.deg2rad(globalValues.az)
            el_rad = np.deg2rad(globalValues.el)
            x_end = globalValues.scanLength * np.cos(el_rad) * np.cos(az_rad)
            y_end = globalValues.scanLength * np.cos(el_rad) * np.sin(az_rad)
            z_end = globalValues.scanLength * np.sin(el_rad)
            scan_line.set_data([0, x_end], [0, y_end])
            scan_line.set_3d_properties([0, z_end])
        return scan_line, marker_plot

    FuncAnimation(fig, update, frames=range(0, 360, 3), interval=50, blit=False)

    plt.show()

# Run everything
combined_gui()
