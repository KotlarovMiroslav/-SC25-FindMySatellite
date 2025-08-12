
# import time
# import serial
# from utils import State
# from globalsConfig import *
# from utils import data_formatter, set_angle

# class TrackState(State):
#     def __init__(self):
#         super().__init__("TRACK")
#         self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
#         self.same_poi_counter = 0
#         self.last_poi = None
#         self.scan_direction = 1
#         self.cur_deg = 0
#         self.last_switch_time = time.time()
#         self.detect_counter = 0  # for live re-detection in TRACK
# def execute(self):
#     global poi, searching, dataOutput

#     cooldown_active = (time.time() - self.last_switch_time) < 2

#     if self.last_poi == poi:
#         self.same_poi_counter += 1
#     else:
#         self.same_poi_counter = 0
#     self.last_poi = poi

#     if not cooldown_active and self.same_poi_counter >= 10:
#         print("[TRACK] Lost target — switching to SEARCH")
#         searching = 1
#         self.last_switch_time = time.time()
#         return "SEARCH"

#     # Initial center position if needed
#     if self.cur_deg != poi * SCAN_STEP and self.same_poi_counter == 0:
#         self.cur_deg = poi * SCAN_STEP

#     # Scan bounds
#     scan_width = 45
#     min_deg = max((poi * SCAN_STEP) - scan_width, 0)
#     max_deg = min((poi * SCAN_STEP) + scan_width, SCAN_MAX_DEG)

#     # Movement
#     if self.scan_direction == 1 and self.cur_deg >= max_deg:
#         self.scan_direction = -1
#         # POI update at the top
#         self._update_poi()
#         # Recalculate new bounds after POI change
#         min_deg = max((poi * SCAN_STEP) - scan_width, 0)
#         max_deg = min((poi * SCAN_STEP) + scan_width, SCAN_MAX_DEG)

#     elif self.scan_direction == -1 and self.cur_deg <= min_deg:
#         self.scan_direction = 1
#         # POI update at the bottom
#         self._update_poi()
#         # Recalculate new bounds after POI change
#         min_deg = max((poi * SCAN_STEP) - scan_width, 0)
#         max_deg = min((poi * SCAN_STEP) + scan_width, SCAN_MAX_DEG)

#     self.cur_deg += self.scan_direction * SCAN_STEP
#     set_angle(self.cur_deg)
#     time.sleep(0.05)

#     return self.name

# def _update_poi(self):
#     """Check LIDAR readings at extreme points and possibly update POI."""
#     global poi, dataOutput

#     try:
#         reading = data_formatter(self.ser.read(9))
#         baseline = dataOutput[int(self.cur_deg / SCAN_STEP)]
#         diff = abs(reading - baseline)

#         if diff >= LIDAR_DIFF_THRESHOLD:
#             self.detect_counter += 1
#             if self.detect_counter >= 3:
#                 new_poi = int(self.cur_deg / SCAN_STEP)
#                 if new_poi != poi:
#                     poi = new_poi
#                     print(f"[TRACK] POI updated to {poi * SCAN_STEP}°")
#                 self.detect_counter = 0
#         else:
#             self.detect_counter = 0

#     except Exception as e:
#         print(f"[TRACK] LIDAR read error during POI update: {e}")


import time
from utils import State
from globalsConfig import *
from utils import set_angle

class TrackState(State):
    def __init__(self):
        super().__init__("TRACK")
        self.cur_deg = 0
        self.scan_direction = 1
        self.same_poi_counter = 0
        self.last_poi = None
        self.last_switch_time = time.time()

    def execute(self):
        global poi, searching, latest_distance

        cooldown_active = (time.time() - self.last_switch_time) < 2

        # Count same POI cycles
        if self.last_poi == poi:
            self.same_poi_counter += 1
        else:
            self.same_poi_counter = 0
        self.last_poi = poi

        # Lost target rule
        if not cooldown_active and self.same_poi_counter >= 10:
            print("[TRACK] Lost target — switching to SEARCH")
            searching = True
            self.last_switch_time = time.time()
            return "SEARCH"

        # Scan around POI
        min_deg = max((poi * SCAN_STEP) - 15, 0)
        max_deg = min((poi * SCAN_STEP) + 15, SCAN_MAX_DEG)

        if self.scan_direction == 1 and self.cur_deg >= max_deg:
            self.scan_direction = -1
        elif self.scan_direction == -1 and self.cur_deg <= min_deg:
            self.scan_direction = 1

        self.cur_deg += self.scan_direction * SCAN_STEP
        set_angle(self.cur_deg)
        time.sleep(0.05)

        # Check for object shift
        with lock:
            distance = latest_distance
        if distance is not None:
            baseline = baseline_data[self.cur_deg // SCAN_STEP]
            diff = abs(distance - baseline)
            if diff >= LIDAR_DIFF_THRESHOLD:
                poi = self.cur_deg // SCAN_STEP
                print(f"[TRACK] POI shifted to {poi * SCAN_STEP}°")

        return self.name
