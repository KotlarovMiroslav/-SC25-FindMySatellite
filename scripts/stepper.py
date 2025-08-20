from time import sleep
import RPi.GPIO as GPIO

ENABLE_PIN = 16
STEP = 20
DIR = 21
MODE = (6, 19, 26)

CW = 1
ACW = 0
SPR = 8*200
delay = 0.0005

RESOLUTION = {
                'Full': (0, 0, 0),
                'Half': (1, 0, 0),
                '1/4':  (0, 1, 0),
                '1/8':  (1, 1, 0),
                '1/16': (0, 0, 1),
                '1/32': (1, 0, 1)
        }

def setup_stepper():

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)
    GPIO.setup(ENABLE_PIN, GPIO.OUT)
    GPIO.setup(MODE, GPIO.OUT)
    GPIO.output(MODE, RESOLUTION['1/8'])
    GPIO.output(ENABLE_PIN, GPIO.HIGH)

def stepper(ANGLE):

    step_count = round(abs((ANGLE / 360) * SPR))
    GPIO.output(ENABLE_PIN, GPIO.LOW)

    if ANGLE > 0:
        GPIO.output(DIR, CW)
    elif ANGLE < 0:
        GPIO.output(DIR, ACW)
    else:
        return

    for _ in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)

    GPIO.output(ENABLE_PIN, GPIO.HIGH)

