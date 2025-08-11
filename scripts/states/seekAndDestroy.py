
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
        self.last_switch_time = time.time()
        self.detect_counter = 0  # for live re-detection in TRACK

    def execute(self):
        global poi, searching, dataOutput

        # Cooldown check to prevent bouncing between SEARCH/TRACK too fast
        cooldown_active = (time.time() - self.last_switch_time) < 2

        # Consecutive same POI check
        if self.last_poi == poi:
            self.same_poi_counter += 1
        else:
            self.same_poi_counter = 0
        self.last_poi = poi

        # If lost target, go back to SEARCH
        if not cooldown_active and self.same_poi_counter >= 10:
            print("[TRACK] Lost target — switching to SEARCH")
            searching = 1
            self.last_switch_time = time.time()
            return "SEARCH"

        # ==== NEW: Start at POI center if POI just changed ====
        if self.cur_deg != poi * SCAN_STEP and self.same_poi_counter == 0:
            self.cur_deg = poi * SCAN_STEP

        # ==== NEW: Configurable scan width ====
        scan_width = 45  # degrees around POI
        min_deg = max((poi * SCAN_STEP) - scan_width, 0)
        max_deg = min((poi * SCAN_STEP) + scan_width, SCAN_MAX_DEG)

        # Scan movement
        if self.scan_direction == 1 and self.cur_deg >= max_deg:
            self.scan_direction = -1
        elif self.scan_direction == -1 and self.cur_deg <= min_deg:
            self.scan_direction = 1

        self.cur_deg += self.scan_direction * SCAN_STEP
        set_angle(self.cur_deg)
        time.sleep(0.05)  # faster updates for smoother tracking

        # LIDAR reading + re-detection
        try:
            reading = data_formatter(self.ser.read(9))
            print(f"[TRACK] Scan@{self.cur_deg}° = {reading}")

            # Re-detection logic from SEARCH
            baseline = dataOutput[int(self.cur_deg / SCAN_STEP)]
            diff = abs(reading - baseline)

            if diff >= LIDAR_DIFF_THRESHOLD:
                self.detect_counter += 1
                if self.detect_counter >= 3:
                    new_poi = int(self.cur_deg / SCAN_STEP)
                    if new_poi != poi:
                        poi = new_poi
                        print(f"[TRACK] POI updated to {poi * SCAN_STEP}°")
                    self.detect_counter = 0
            else:
                self.detect_counter = 0

        except Exception as e:
            print(f"[TRACK] LIDAR read error: {e}")

        return self.name
