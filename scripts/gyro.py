import time
import board
import busio
import adafruit_bno055

# Initialize I2C and BNO055 sensor

def setup_gyro():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_bno055.BNO055_I2C(i2c)
    return sensor

def angle_to_north(heading):
    if heading is None:
        return "Sensor not calibrated yet."

    # Normalize heading to [0, 360)
    heading = heading % 360

    # Calculate angle difference to North (100° for some reason lol)
    diff = (0 - heading) % 360

    # Decide if it's better to turn Left or Right
    if diff == 0:
        return "You are facing North."
    elif diff < 180:
        return f"Turn {diff:.1f}° to the RIGHT to face North."
    else:
        return f"Turn {(360 - diff):.1f}° to the LEFT to face North."

def input_angle(heading):
    if heading is None:
        return "Sensor botched lol."

    heading = heading % 360 # keep the heading angle between 0 and 360 degrees
    diff = (0 - heading) % 360 # the angle required to reach north

    if diff == 0:
        diff = 0
        return diff
    elif diff < 180:
        return diff
    else:
        diff = (-1) * (360 - diff)
        return diff