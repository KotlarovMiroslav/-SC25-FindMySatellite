from matplotlib.widgets import Button
from sgp4.api import Satrec
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (needed for 3D plot)
import datetime as dt
from sgp4.api import Satrec, jday



def gui():
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")

    # scale so Earth (~6371 km) fits into ~400 units
    scale_factor = 400 / 7000.0
    ax.set_xlim([-400, 400])
    ax.set_ylim([-400, 400])
    ax.set_zlim([-400, 400])

    tle_lines = []

    # --- Buttons ---
    btn_ax = plt.axes([0.1, 0.01, 0.15, 0.05])
    btn_tle = Button(btn_ax, "Load TLE")

    clear_ax = plt.axes([0.3, 0.01, 0.15, 0.05])
    btn_clear = Button(clear_ax, "Clear TLEs")

    # --- Load and plot TLE ---
    def load_tle(event):
        try:
            with open("C:\\xampp\\htdocs\\18122\\Python\\1.PrepClass\\stage\\FindMySatellite_SC25\\scripts\\testGUI\\TLE.txt", "r") as f:
                lines = f.read().splitlines()
            if len(lines) < 3:
                print("TLE file must have 3 lines (name + 2 lines)")
                return

            name = lines[0].strip()
            line1 = lines[1].strip()
            line2 = lines[2].strip()

            sat = Satrec.twoline2rv(line1, line2)
            start = dt.datetime.utcnow()

            ts = np.linspace(0, 24*60, 200)  # 24 hours, 200 samples
            xs, ys, zs = [], [], []

            for minutes in ts:
                current = start + dt.timedelta(minutes=float(minutes))
                jd, fr = jday(current.year, current.month, current.day,
                            current.hour, current.minute, current.second + current.microsecond*1e-6)
                e, r, v = sat.sgp4(jd, fr)
                if e == 0:
                    xs.append(r[0] * scale_factor)
                    ys.append(r[1] * scale_factor)
                    zs.append(r[2] * scale_factor)

            line, = ax.plot(xs, ys, zs, label=name, color="orange")
            print(xs[:5], ys[:5], zs[:5])
            tle_lines.append(line)
            ax.legend()
            plt.draw()

        except Exception as e:
            print("Error reading TLE:", e)

    btn_tle.on_clicked(load_tle)

    # --- Clear plotted orbits ---
    def clear_tles(event):
        for line in tle_lines:
            line.remove()
        tle_lines.clear()
        plt.draw()

    btn_clear.on_clicked(clear_tles)

    # --- Optional animation hook ---
    # def update(frame):
    #     return []
    # Earth sphere for reference (scaled to ~387 units radius)
    
    #FuncAnimation(fig, update, frames=range(0, 360, 3), interval=50, blit=False)
    plt.show()



gui()
