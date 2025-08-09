def parse_tle_line2(line2):
    """
    Extracts 5 orbital parameters from TLE Line 2.
    """
    inclination = float(line2[8:16].strip())
    raan = float(line2[17:25].strip())
    eccentricity = float("0." + line2[26:33].strip())
    arg_perigee = float(line2[34:42].strip())
    mean_anomaly = float(line2[43:51].strip())

    return {
        "Inclination (deg)": inclination,
        "RAAN (deg)": raan,
        "Eccentricity": eccentricity,
        "Argument of Perigee (deg)": arg_perigee,
        "Mean Anomaly (deg)": mean_anomaly
    }

def main():
    print("📥 Paste the full TLE block (3 lines). When you're done, type 'done' and press Enter.\n")

    lines = []
    while True:
        line = input()
        if line.strip().lower() == 'done':
            break
        lines.append(line.strip())

    if len(lines) != 3:
        print("❌ Error: You must enter exactly 3 lines (Name, Line 1, Line 2).")
        return

    line2 = lines[2]
    if not line2.startswith("2 "):
        print("❌ Error: Third line must be TLE Line 2 starting with '2 '.")
        return

    elements = parse_tle_line2(line2)

    print("\n✅ Extracted Orbital Elements:")
    for key, value in elements.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
