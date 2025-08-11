import serial
import time
import RPi.GPIO as GPIO
import threading
import threading
curDeg = 1
passedStep = 0
objectSpotted = 0
envScanned = 0
searching = 1
poi = -1
dataOutput = []
globalReading = 0

#Set up the pins of the raspberry
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 50)
pwm.start(0)

lock = threading.Lock()

SCAN_MAX_DEG = 60
SCAN_STEP = 5
LIDAR_DIFF_THRESHOLD = 60

SERIAL_PORT = "/dev/serial0"
SERIAL_BAUDRATE = 115200