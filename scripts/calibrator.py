#from servo import set_angle
import time
import serial
import RPi.GPIO as GPIO
import threading
from stepper import setup_stepper, stepper
from gyro import setup_gyro, angle_to_north, input_angle
import board
import busio
import adafruit_bno055
import math

def set_angle(angle):
    duty = 1.5 + (angle / 180) * 10
    pwm.ChangeDutyCycle(duty)
    #time.sleep(0.1)

try:
    sensor = setup_gyro()
    setup_stepper()

    time.sleep(0.5)

    # servo setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(18, GPIO.OUT)
    pwm = GPIO.PWM(18, 50)
    pwm.start(0)

    # Manual calibration (10 seconds)
    """
    for i in range(20):
        heading = sensor.euler[0] # Yaw angle in degrees (0° is North)
        message = angle_to_north(heading)
        print(message)
        time.sleep(0.5)
    """

    # Calibration

    stepper(1)
    set_angle(45)

    time.sleep(0.5)

    for j in range(0, 5):

        for i in range(361):
            if i < 181:
                stepper(-1)
                set_angle(45*math.sin(math.radians(i*2)) + 45)
            else:
                stepper(1)
                set_angle(45*math.sin(math.radians(i*2)) + 45)

        time.sleep(0.2)

    time.sleep(0.5)

    print("Calibration Finished!")

    # Movement of stepper

    ANGLE = input_angle(sensor.euler[0])

    print(ANGLE)
    time.sleep(1)
    stepper(ANGLE)

    time.sleep(2)

    set_angle(0)

    time.sleep(1)

    print("North position reached!")
    """
    set_angle(pwm, 60)
    time.sleep(1)
    set_angle(pwm, 0)
    """
except KeyboardInterrupt:
    print("Interrupted")

finally:
    GPIO.cleanup()