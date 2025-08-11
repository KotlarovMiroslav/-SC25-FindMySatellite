from globalsConfig import *
from utils import data_formatter
from utils.classes import State

class SearchState(State):
    def __init__(self):
        super().__init__("SEARCH")
        self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
        self.curPos = 0

    def execute(self):
        global dataOutput, passedStep, envScanned, curDeg, searching, poi

        try:
            reading = data_formatter(self.ser.read(9))
        except Exception:
            return self.name  # stay in SEARCH if bad read

        with lock:
            if envScanned == 1 and passedStep == 1:
                if searching:
                    if self.curPos >= len(dataOutput):
                        self.curPos = 0
                    baseline = dataOutput[self.curPos]
                    diff = abs(reading - baseline)
                    if diff >= LIDAR_DIFF_THRESHOLD:
                        searching = 0
                        poi = self.curPos
                        print(f"OBJECT DETECTED at {poi*SCAN_STEP}°")
                        return "TRACK"
                    else:
                        self.curPos += 1
                passedStep = 0

            elif passedStep == 1:
                dataOutput.append(reading)
                print(f"Scan@{curDeg}° = {reading}")
                passedStep = 0
                if curDeg >= SCAN_MAX_DEG:
                    envScanned = 1
                    print("INITIAL SCAN COMPLETE — Entering Detection Mode")

        return self.name