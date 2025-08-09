def run_lidar():
    global dataOutput, passedStep, lock, envScanned, curDeg, searching, poi
    ser = serial.Serial("/dev/serial0", 115200)
    curPos = 0

    while True:
        try:
            reading = data_formatter(ser.read(9))
        except Exception:
            continue  # Skip corrupted reads

        with lock:
            if envScanned == 1 and passedStep == 1:
                if searching:
                    if curPos >= len(dataOutput):
                        curPos = 0
                    baseline = dataOutput[curPos]
                    diff = abs(reading - baseline)
                    if diff > 65:
                        searching = 0
                        poi = curPos
                        print(f"OBJECT DETECTED at {poi*5}°")
                    else:
                        curPos += 1
                else:
                    min_poi = max(poi - 3, 2)
                    max_poi = min(poi + 2, len(dataOutput) - 2)
                    baseline = dataOutput[curPos]
                    diff = abs(reading - baseline)
                    if diff > 65:
                        print(f"Scan:{reading},Base: {baseline} ,Diff:{diff}")
                        poi = curPos
                        print(f"POI SHIFTED — New center: {poi*5}°")
                    curPos += 1
                    if curPos > max_poi:
                        curPos = min_poi
                passedStep = 0

            elif passedStep == 1:
                dataOutput.append(reading)
                print(f"Scan@{curDeg}° = {reading}")
                passedStep = 0
                if curDeg >= 60:
                    envScanned = 1
                    print("INITIAL SCAN COMPLETE — Entering Detection Mode")
