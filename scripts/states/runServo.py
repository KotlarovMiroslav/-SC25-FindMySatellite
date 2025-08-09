def run_servo():
    global passedStep, lock, curDeg, searching
    try:
        while True:
            for degree in range(0, 65, 5):
                with lock:
                    if searching == 0:
                        return
                    while passedStep != 0:
                        pass
                set_angle(degree)
                curDeg = degree
                #time.sleep(0.1)
                with lock:
                    passedStep = 1
                time.sleep(0.095)
    except KeyboardInterrupt:
        pwm.stop()
        GPIO.cleanup()