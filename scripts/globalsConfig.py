import serial
import time
import RPi.GPIO as GPIO
import threading

curDeg = 1
passedStep = 0
objectSpotted = 0
envScanned = 0
searching = 1
poi = -1
dataOutput = []

lock = threading.Lock()
