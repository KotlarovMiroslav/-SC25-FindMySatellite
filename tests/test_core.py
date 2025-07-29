import unittest
from satellite_tracker.core import SatelliteTracker

class TestSatelliteTracker(unittest.TestCase):
    def test_process_frame(self):
        tracker = SatelliteTracker()
        dummy_data = [(0, 0, 1), (1, 1, 2), (2, 2, 10)]
        result = tracker.process_lidar_frame(dummy_data)
        self.assertEqual(result, (2, 2, 10))

if __name__ == '__main__':
    unittest.main()
