import serial
from globalsConfig import *
from utils import data_formatter

def lidar_reader():
    """ Continuously reads LIDAR and stores the latest distance """
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
    while True:
        try:
            reading = data_formatter(ser.read(9))
            with lock:
                latest_distance = reading
        except Exception:
            continue