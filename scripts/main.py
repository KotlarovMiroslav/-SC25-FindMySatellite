from globalsConfig import GPIO
from states.runLidar import SearchState
from states.runServo import ScanState
from states.seekAndDestroy import TrackState
from utils.classes import Operator
from globalsConfig import *

if __name__ == "__main__":
    try:
        op = Operator(
            states={
                "SEARCH": SearchState.execute(),
                "TRACK": TrackState.execute(),
                "SCAN": ScanState.execute()
            },
            start_state="SEARCH"
        )
        op.run()
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()
        print("done")
