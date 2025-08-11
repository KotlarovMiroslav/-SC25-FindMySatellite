import threading
from globalsConfig import GPIO
from states.runLidar import SearchState
from states.runServo import ScanState
from states.seekAndDestroy import TrackState
from utils.classes import Operator
#Set up the pins of the raspberry
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 50)
pwm.start(0)

if __name__ == "__main__":
    try:
        op = Operator(
            states={
                "SEARCH": SearchState(),
                "TRACK": TrackState(),
                "SCAN": ScanState()
            },
            start_state="SEARCH"
        )
        op.run()
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()
        print("done")
