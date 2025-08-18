# Stepper function code that has variable step size, (1 is step size 1.8, 32 is step size 1.8/32 etc)
# Note that positive values of ANGLE given as input turn stepper ANTICLOCKWISE and vice versa
# My main issue with the code is that we have to call the setup_stepper function with the step size every time you want to change the size of the steps but i guess this isn't a huge issue for now?

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

live_angle = 0

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
    global live_angle
    GPIO.output(ENABLE_PIN, GPIO.LOW)

    SPR = 200*SIZE

    step_count = round(abs((ANGLE / 360) * SPR))

    if ANGLE > 0:
        GPIO.output(DIR, ACW)
    elif ANGLE < 0:
        GPIO.output(DIR, CW)
    else:
        return

    live_angle = round(live_angle + ((ANGLE/360) * SPR)*(1.8/SIZE), 2)

    for _ in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)

    GPIO.output(ENABLE_PIN, GPIO.HIGH)
