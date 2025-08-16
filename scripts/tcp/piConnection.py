import socket
import time


LAPTOP_IP = "192.168.55.129"  # replace with your laptop's IP
PORT = 5005

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((LAPTOP_IP, PORT))
print("Connected to laptop")
az = 0
while True:
    # Example data (replace with real LiDAR + motor values)
    el = 30
    az = az + 1
    if az == 180:
        az = 0
    distance = 250
    
    msg = f"{el}, {az}, {distance}, "
    client.send(msg.encode())

    time.sleep(0.1)  # ~20 updates per second
