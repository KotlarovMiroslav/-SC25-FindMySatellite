from time import sleep
import RPi.GPIO as GPIO

ENABLE_PIN = 16
STEP = 20
DIR = 21
MODE = (6, 19, 26)

CW = 1
ACW = 0
SPR = 200
delay = 0.0005

def setup_stepper(SIZE):

    RESOLUTION = {
                '1': (0, 0, 0),
                '1/2': (1, 0, 0),
                '1/4':  (0, 1, 0),
                '1/8':  (1, 1, 0),
                '1/16': (0, 0, 1),
                '1/32': (1, 0, 1)
        }

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)
    GPIO.setup(ENABLE_PIN, GPIO.OUT)
    GPIO.setup(MODE, GPIO.OUT)

    if SIZE == 1:
        GPIO.output(MODE, RESOLUTION['1'])
    elif SIZE == 2:
        GPIO.output(MODE, RESOLUTION['1/2'])
    elif SIZE == 4:
        GPIO.output(MODE, RESOLUTION['1/4'])
    elif SIZE == 8:
        GPIO.output(MODE, RESOLUTION['1/8'])
    elif SIZE == 16:
        GPIO.output(MODE, RESOLUTION['1/16'])
    else:
        GPIO.output(MODE, RESOLUTION['1/32'])

    GPIO.output(ENABLE_PIN, GPIO.HIGH)

def stepper(ANGLE, SIZE):

    step_count = round(abs((ANGLE / 360) * SPR))
    GPIO.output(ENABLE_PIN, GPIO.LOW)

    if SIZE == 1:
        SPR = 200 * 1
    elif SIZE == 2:
        SPR = 200 * 2
    elif SIZE == 4:
        SPR = 200 * 4
    elif SIZE == 8:
        SPR = 200 * 8
    elif SIZE == 16:
        SPR = 200 * 16
    else:
        SPR = 200 * 32

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