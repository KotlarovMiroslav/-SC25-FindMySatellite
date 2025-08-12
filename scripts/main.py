# import threading
# from globalsConfig import GPIO
# from states.runLidar import SearchState
# from states.runServo import ScanState
# from states.seekAndDestroy import TrackState
# from utils.classes import Operator
# from globalsConfig import *

# if __name__ == "__main__":
#     try:
#         t_lidar = threading.Thread(target=lidar_reader, daemon=True)
#         t_lidar.start()
#         op = Operator(
#             states={
#                 "SEARCH": SearchState.execute(),
#                 "TRACK": TrackState.execute(),
#                 "SCAN": ScanState.execute()
#             },
#             start_state="SEARCH"
#         )
#         op.run()
#     except KeyboardInterrupt:
#         pwm.stop()
#         GPIO.cleanup()
#         print("done")

import threading
from globalsConfig import pwm,GPIO
from utils import lidar_reader
from utils import Operator
from states import runLidar
from states import seekAndDestroy

if __name__ == "__main__":
    try:
        # Start LIDAR thread
        t_lidar = threading.Thread(target=lidar_reader, daemon=True)
        t_lidar.start()

        # State machine
        sm = Operator(
            states={
                "SEARCH": runLidar(),
                "TRACK": seekAndDestroy()
            },
            start_state="SEARCH"
        )
        sm.run()

    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()
        print("Shutdown complete")
