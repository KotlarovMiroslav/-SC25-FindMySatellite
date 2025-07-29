from .utils import distance
import time

class SatelliteTracker:
    def __init__(self):
        self.history = []

    def process_lidar_frame(self, points):
        target = self.detect_target(points)
        self.history.append((time.time(), target))
        return target

    def detect_target(self, points):
        return max(points, key=lambda p: p[2])

    def calculate_trajectory(self):
        if len(self.history) < 2:
            return None
        (t1, p1), (t2, p2) = self.history[-2:]
        dt = t2 - t1
        velocity = [(p2[i] - p1[i]) / dt for i in range(3)]
        return velocity
