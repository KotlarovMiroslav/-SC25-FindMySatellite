from satellite_tracker.core import SatelliteTracker
import random

def simulate_lidar_data():
    return [(random.uniform(0, 50), random.uniform(0, 50), random.uniform(0, 20)) for _ in range(100)]

if __name__ == "__main__":
    tracker = SatelliteTracker()
    for _ in range(10):
        frame = simulate_lidar_data()
        target = tracker.process_lidar_frame(frame)
        trajectory = tracker.calculate_trajectory()
        print(f"Target: {target}")
        if trajectory:
            print(f"Estimated velocity: {trajectory}")
