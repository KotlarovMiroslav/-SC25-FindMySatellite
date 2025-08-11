# states/track_state.py
import time
import serial
from utils import State
from globalsConfig import *
from utils import data_formatter, set_angle

class TrackState(State):
    def __init__(self):
        super().__init__("TRACK")
        self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
        self.same_poi_counter = 0
        self.last_poi = None
        self.scan_direction = 1
        self.cur_deg = 0
        self.last_switch_time = time.time()  # cooldown timer start

    def execute(self):
        global poi, searching

        # Cooldown check: don't switch back to SEARCH too quickly
        cooldown_active = (time.time() - self.last_switch_time) < 2

        # Consecutive same POI counting
        if self.last_poi == poi:
            self.same_poi_counter += 1
        else:
            self.same_poi_counter = 0
        self.last_poi = poi

        # Lost target → go back to SEARCH (if cooldown expired)
        if not cooldown_active and self.same_poi_counter >= 10:
            print("[TRACK] Lost target — switching to SEARCH")
            searching = 1
            self.last_switch_time = time.time()
            return "SEARCH"

        # Tracking scan around POI
        min_deg = max((poi * SCAN_STEP) - 15, 0)
        max_deg = min((poi * SCAN_STEP) + 15, SCAN_MAX_DEG)

        if self.scan_direction == 1 and self.cur_deg >= max_deg:
            self.scan_direction = -1
        elif self.scan_direction == -1 and self.cur_deg <= min_deg:
            self.scan_direction = 1

        self.cur_deg += self.scan_direction * SCAN_STEP
        set_angle(self.cur_deg)
        time.sleep(0.1)

        # LIDAR reading
        try:
            reading = data_formatter(self.ser.read(9))
            print(f"[TRACK] Scan@{self.cur_deg}° = {reading}")
        except Exception:
            pass  # ignore bad reads

        return self.name
