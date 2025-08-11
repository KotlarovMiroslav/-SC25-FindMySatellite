from globalsConfig import *
from utils import data_formatter

def run_lidar():
    global dataOutput, passedStep, lock, envScanned, curDeg, searching, poi, globalReading
    ser = serial.Serial("/dev/serial0", 115200)
    curPos = 0

    while True:
        try:
            reading = data_formatter(ser.read(9))
            with lock:
                globalReading = reading
                pass
        except Exception:
            continue  # Skip corrupted reads

        with lock:
            if envScanned == 1 and passedStep == 1:
                if searching:
                    if curPos >= len(dataOutput):
                        curPos = 0
                    baseline = dataOutput[curPos]
                    diff = abs(reading - baseline)
                    if diff > 100:
                        searching = 0
                        poi = curPos
                        print(f"OBJECT DETECTED at {poi*5}°")
                    else:
                        curPos += 1
                passedStep = 0

            elif passedStep == 1:
                dataOutput.append(reading)
                print(f"Scan@{curDeg}° = {reading}")
                passedStep = 0
                if curDeg >= 60:
                    envScanned = 1
                    print("INITIAL SCAN COMPLETE — Entering Detection Mode")
