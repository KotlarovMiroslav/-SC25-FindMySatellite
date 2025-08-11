from globalsConfig import pwm
def set_angle(angle):
    duty = 1.5 + (angle / 180) * 10
    pwm.ChangeDutyCycle(duty)
    #time.sleep(0.1)