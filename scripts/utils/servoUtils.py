from globalsConfig import pwm
# script.py
import sys
import os
import time

# get the parent directory of utils
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

def set_angle(angle):
    duty = 1.5 + (angle / 180) * 10
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.055)