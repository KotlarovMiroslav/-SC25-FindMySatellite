import serial
import time
import RPi.GPIO as GPIO
import threading

# Global state variables
curDeg = 1
passedStep = 0
objectSpotted = 0
envScanned = 0
searching = 1
poi = -1
dataOutput = []

lock = threading.Lock()

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 50)
pwm.start(0)

# --- Utility functions ---

def set_angle(angle):
    duty = 1.5 + (angle / 180) * 10
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)

def data_formatter(data_bytes):
    if isinstance(data_bytes, bytes):
        data = list(data_bytes)
    elif isinstance(data_bytes, list) and len(data_bytes) == 9:
        data = data_bytes
    else:
        raise ValueError("Input must be a 9-byte sequence.")

    if data[0] != 0x59 or data[1] != 0x59:
        raise ValueError("Invalid frame header.")

    checksum = sum(data[:8]) & 0xFF
    if checksum != data[8]:
        raise ValueError("Checksum mismatch.")

    distance = float((data[3] << 8) | data[2])
    return distance

# --- Main Threads ---

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
                    if diff > 40:
                        searching = 0
                        poi = curPos
                        print(f"OBJECT DETECTED at {poi*5}°")
                    else:
                        curPos += 1
                else:
                    min_poi = max(poi - 2, 0)
                    max_poi = min(poi + 2, len(dataOutput) - 1)
                    baseline = dataOutput[curPos]
                    diff = abs(reading - baseline)
                    if diff > 40:
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
                if curDeg >= 55:
                    envScanned = 1
                    print("INITIAL SCAN COMPLETE — Entering Detection Mode")

def run_servo():
    global passedStep, lock, curDeg, searching
    try:
        while True:
            for degree in range(0, 60, 5):
                with lock:
                    if searching == 0:
                        return
                    while passedStep != 0:
                        pass
                set_angle(degree)
                curDeg = degree
                time.sleep(0.3)
                with lock:
                    passedStep = 1
                time.sleep(0.1)
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()

def seekAndDestroy():
    global passedStep, lock, curDeg, searching, dataOutput, poi
    while True:
        if searching == 0:
            print(f"TRACKING POI around {poi*5}°")
            min_deg = max((poi * 5) - 10, 0)
            max_deg = min((poi * 5) + 10, 60)
            for degree in range(min_deg, max_deg + 1, 5):
                with lock:
                    while passedStep != 0:
                        pass
                set_angle(degree)
                curDeg = degree
                time.sleep(0.3)
                with lock:
                    passedStep = 1
                time.sleep(0.1)

# --- Main Program ---

try:
    t1 = threading.Thread(target=run_lidar)
    t2 = threading.Thread(target=run_servo)
    t3 = threading.Thread(target=seekAndDestroy)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
    print("done")
