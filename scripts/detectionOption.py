from time import sleep
import RPi.GPIO as GPIO
import numpy as np
import serial

# ------------------- PINS -------------------
ENABLE_PIN = 16
STEP = 20
DIR = 21
MODE = (6, 19, 26)
SERVO_PIN = 18

# ------------------- SETTINGS -------------------
CW = 1
ACW = 0
SPR = 200 * 32
DELAY = 0.00005
ANGLE = 200
MAX_DISTANCE = 7.0   # ignore points beyond this
NOISE_THRESHOLD = 0.2  # meters for detection
SERVO_FIXED = 150     # fixed angle

# ------------------- GPIO SETUP -------------------
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(ENABLE_PIN, GPIO.OUT)
GPIO.setup(MODE, GPIO.OUT)
RESOLUTION = {
    'Full':  (0, 0, 0),
    'Half':  (1, 0, 0),
    '1/4':   (0, 1, 0),
    '1/8':   (1, 1, 0),
    '1/16':  (0, 0, 1),
    '1/32':  (1, 0, 1)
}
GPIO.output(MODE, RESOLUTION['1/32'])

GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

# ------------------- FUNCTIONS -------------------
def move_stepper_one_step(direction):
    GPIO.output(DIR, direction)
    GPIO.output(ENABLE_PIN, GPIO.LOW)
    GPIO.output(STEP, GPIO.HIGH)
    sleep(DELAY)
    GPIO.output(STEP, GPIO.LOW)
    sleep(DELAY)
    GPIO.output(ENABLE_PIN, GPIO.HIGH)

def set_servo_angle(angle):
    duty = 2.5 + (angle / 180) * (12.5 - 2.5)
    servo.ChangeDutyCycle(duty)
    sleep(0.5)
    servo.ChangeDutyCycle(0)

# ------------------- TFmini SETUP -------------------
lidar = serial.Serial('/dev/ttyS0', 115200, timeout=0.1)

def read_lidar():
    """Read TFmini distance in meters"""
    if lidar.in_waiting >= 9:
        data = lidar.read(9)
        if data[0] == 0x59 and data[1] == 0x59:
            distance = data[2] + data[3]*256
            return distance / 100.0
    return None

# ------------------- MAIN BASELINE -------------------
try:
    print("Initializing baseline...")
    baseline = []

    set_servo_angle(SERVO_FIXED)
    step_count = round((ANGLE / 360) * SPR)

    # Two sweeps: 0->200 and 200->0
    for repeat in range(2):
        for direction in [CW, ACW]:
            for step in range(step_count + 1):
                current_angle = (step / step_count) * ANGLE
                if direction == ACW:
                    current_angle = ANGLE - current_angle

                move_stepper_one_step(direction)
                d = read_lidar()
                if d is not None and d <= MAX_DISTANCE:
                    baseline.append([round(current_angle,2), round(d,2)])
                    print(f"Baseline - Stepper: {current_angle:.2f}°, Distance: {d:.2f} m")

    baseline = np.array(baseline)
    print(f"Baseline initialized with {len(baseline)} points.")

    # ------------------- CONTINUOUS SCAN -------------------
    while True:
        for direction in [CW, ACW]:
            for step in range(step_count + 1):
                current_angle = (step / step_count) * ANGLE
                if direction == ACW:
                    current_angle = ANGLE - current_angle

                move_stepper_one_step(direction)
                d = read_lidar()
                if d is not None and d <= MAX_DISTANCE:
                    idx = np.argmin(np.abs(baseline[:,0] - current_angle))
                    baseline_distance = baseline[idx,1]

                    print(f"Stepper: {current_angle:.2f}°, Distance: {d:.2f} m")

                    # Detect moving object
                    if abs(d - baseline_distance) > NOISE_THRESHOLD:
                        print(f"*** Drone detected at Stepper {current_angle:.2f}°, Distance change {d - baseline_distance:.2f} m ***")
                        print("Stopping stepper!")
                        raise KeyboardInterrupt  # stop scanning immediately

except KeyboardInterrupt:
    print("Scanning stopped.")

finally:
    servo.stop()
    GPIO.cleanup()
    lidar.close()
