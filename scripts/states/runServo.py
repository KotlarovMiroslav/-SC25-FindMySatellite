import time
from globalsConfig import *
from utils import set_angle
from utils.classes import State

class ScanState(State):
    def __init__(self):
        super().__init__("SCAN")

    def execute(self):
        global passedStep, curDeg, searching
        for degree in range(0, SCAN_MAX_DEG + 5, SCAN_STEP):
            with lock:
                if searching == 0:
                    return "TRACK"
                while passedStep != 0:
                    pass
            set_angle(degree)
            curDeg = degree
            with lock:
                passedStep = 1
            time.sleep(0.095)
        return self.name