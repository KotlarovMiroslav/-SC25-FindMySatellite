import serial
import time
from utils import State
from globalsConfig import *
from utils import data_formatter, set_angle

class SearchState(State):
    def __init__(self):
        super().__init__("SEARCH")
        self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
        self.cur_deg = 0
        self.cur_pos = 0
        self.baseline_scan_done = False

    def execute(self):
        global dataOutput, poi, searching

        # Sweep servo
        if self.cur_deg > SCAN_MAX_DEG:
            self.cur_deg = 0

        set_angle(self.cur_deg)
        time.sleep(0.1)  # give servo time to move

        try:
            reading = data_formatter(self.ser.read(9))
        except Exception:
            # If bad read, skip this cycle
            self.cur_deg += SCAN_STEP
            return self.name

        # Baseline scan phase
        if not self.baseline_scan_done:
            dataOutput.append(reading)
            print(f"[SEARCH] Baseline Scan @ {self.cur_deg}° = {reading}")
            self.cur_deg += SCAN_STEP
            if self.cur_deg > SCAN_MAX_DEG:
                self.baseline_scan_done = True
                searching = 1
                print("[SEARCH] Baseline complete, entering detection mode")
            return self.name

        # Detection phase
        if self.cur_pos >= len(dataOutput):
            self.cur_pos = 0
        baseline = dataOutput[self.cur_pos]
        diff = abs(reading - baseline)

        if diff >= LIDAR_DIFF_THRESHOLD:
            searching = 0
            poi = self.cur_pos
            print(f"[SEARCH] OBJECT DETECTED at {poi * SCAN_STEP}°")
            return "TRACK"

        self.cur_pos += 1
        self.cur_deg += SCAN_STEP
        return self.name