import time
from globalsConfig import *
from utils import set_angle
from utils.classes import State

class TrackState(State):
    def __init__(self):
        super().__init__("TRACK")
        self.same_poi_counter = 0
        self.last_poi = None

    def execute(self):
        global passedStep, curDeg, searching, poi

        if self.last_poi == poi:
            self.same_poi_counter += 1
        else:
            self.same_poi_counter = 0

        self.last_poi = poi

        if self.same_poi_counter >= 10:
            print("[TRACK] Lost target — returning to SEARCH")
            searching = 1
            return "SEARCH"

        print(f"TRACKING POI around {poi*SCAN_STEP}°")
        min_deg = max((poi * SCAN_STEP) - 15, 0)
        max_deg = min((poi * SCAN_STEP) + 15, SCAN_MAX_DEG)

        for degree in range(max_deg + 1, min_deg, -SCAN_STEP):
            with lock:
                while passedStep != 0:
                    pass
            set_angle(degree)
            curDeg = degree
            with lock:
                passedStep = 1
            time.sleep(0.06)

        for degree in range(min_deg, max_deg + 1, SCAN_STEP):
            with lock:
                while passedStep != 0:
                    pass
            set_angle(degree)
            curDeg = degree
            with lock:
                passedStep = 1
            time.sleep(0.06)

        return self.name