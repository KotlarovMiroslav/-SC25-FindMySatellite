import socket
import time

import globalsConfig as gv

LAPTOP_IP = "192.168.55.129"  # replace with your laptop's IP
PORT = 5005

def pi_connection():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((LAPTOP_IP, PORT))
        print("Connected to laptop")
        gv.ready_state = 1
    except Exception as e:
        print("[ERROR] pi_connection crashed:", e, flush=True)
    while True:
        # Example data (replace with real LiDAR + motor values)
        
        el = gv.servo_pos
        az = gv.stepper_pos
        distance = gv.latest_distance + 100
        
        msg = f"{el}, {az}, {distance}, "
        #print(msg)
        client.send(msg.encode())

        time.sleep(0.02)  # ~20 updates per second
