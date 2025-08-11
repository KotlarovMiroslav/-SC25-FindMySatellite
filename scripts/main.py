import threading
from globalsConfig import GPIO
from states import runLidar, runServo, seekAndDestroy

#Set up the pins of the raspberry
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 50)
pwm.start(0)

if __name__ == "__main__":
    try:
        # Create threads for each state
        t1 = threading.Thread(target=runLidar)
        t2 = threading.Thread(target=runServo)
        t3 = threading.Thread(target=seekAndDestroy)

        # Start them
        t1.start()
        t2.start()
        t3.start()

        # Keep main thread alive
        t1.join()
        t2.join()
        t3.join()

    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()
        print("done")
