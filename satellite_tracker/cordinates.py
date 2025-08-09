from sgp4.api import Satrec, jday
import numpy as np

def main():
    print("📥 Paste your full TLE (3 lines), then type 'done':")
    
    tle_lines = []
    while True:
        line = input()
        if line.strip().lower() == 'done':
            break
        tle_lines.append(line.strip())

    if len(tle_lines) != 3:
        print("❌ You must enter exactly 3 lines: name, line1, and line2.")
        return

    name = tle_lines[0]
    line1 = tle_lines[1]
    line2 = tle_lines[2]

    # Create satellite object
    satellite = Satrec.twoline2rv(line1, line2)

    print("\n📆 Enter the date and time you want the satellite position for:")
    year = int(input("Year (e.g., 2025): "))
    month = int(input("Month (1-12): "))
    day = int(input("Day: "))
    hour = int(input("Hour (0-23): "))
    minute = int(input("Minute (0-59): "))
    second = float(input("Second (e.g., 30.0): "))

    # Convert to Julian date
    jd, fr = jday(year, month, day, hour, minute, second)

    # Propagate using SGP4
    error_code, position_km, velocity_kmps = satellite.sgp4(jd, fr)

    if error_code != 0:
        print(f"❌ Error: SGP4 failed with code {error_code}.")
        return

    # Convert to meters
    x, y, z = [coord * 1000 for coord in position_km]
    vx, vy, vz = [v * 1000 for v in velocity_kmps]

    print(f"\n🛰 Satellite: {name}")
    print("🌍 Cartesian ECI Position (meters):")
    print(f"  x = {x:.2f}")
    print(f"  y = {y:.2f}")
    print(f"  z = {z:.2f}")

    # Spherical coordinates
    rho = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arctan2(y, x)  # radians
    phi = np.arccos(z / rho)  # radians

    print("\n🌐 Spherical Coordinates:")
    print(f"  ρ (radius)     = {rho:.2f} m")
    print(f"  θ (azimuth)    = {np.degrees(theta):.2f}°")
    print(f"  φ (polar angle)= {np.degrees(phi):.2f}°")

    # Velocity magnitude
    v_m = np.sqrt(vx**2 + vy**2 + vz**2)
    print(f"\n🚀 Speed (v) = {v_m:.2f} m/s")

    # Semi-major axis using Vis-Viva
    mu = 3.986e14  # Earth's gravitational parameter in m^3/s^2
    a = 1 / ((2 / rho) - (v_m**2 / mu))
    print(f"\n📏 Semi-major axis (a): {a:.2f} m")

if __name__ == "__main__":
    main()
