import time
from utils import State
from globalsConfig import *
from utils import data_formatter, set_angle
import serial

class TrackState(State):
    def __init__(self):
        super().__init__("TRACK")
        self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
        self.same_poi_counter = 0
        self.last_poi = None
        self.scan_direction = 1
        self.cur_deg = 0

    def execute(self):
        global poi, searching

        # If we're tracking the same poi, count it
        if self.last_poi == poi:
            self.same_poi_counter += 1
        else:
            self.same_poi_counter = 0
        self.last_poi = poi

        # Lost target after 10 consecutive detections in same spot
        if self.same_poi_counter >= 10:
            print("[TRACK] Lost target — switching to SEARCH")
            searching = 1
            return "SEARCH"

        # Determine scan range
        min_deg = max((poi * SCAN_STEP) - 15, 0)
        max_deg = min((poi * SCAN_STEP) + 15, SCAN_MAX_DEG)

        # Move servo
        if self.scan_direction == 1 and self.cur_deg >= max_deg:
            self.scan_direction = -1
        elif self.scan_direction == -1 and self.cur_deg <= min_deg:
            self.scan_direction = 1

        self.cur_deg += self.scan_direction * SCAN_STEP
        set_angle(self.cur_deg)
        time.sleep(0.1)  # allow servo movement

        # Read LIDAR
        try:
            reading = data_formatter(self.ser.read(9))
        except Exception:
            return self.name

        print(f"[TRACK] Scan@{self.cur_deg}° = {reading}")

        return self.name