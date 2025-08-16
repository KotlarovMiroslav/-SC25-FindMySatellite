import socket
import globalValues 

def communicate_with_pi():
    #az, el, scanLength, readyToPlot
    HOST = "0.0.0.0"  # listen on all interfaces
    PORT = 5005       # choose any free port

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)

    print("Waiting for Pi to connect...")
    conn, addr = server.accept()
    print(f"Connected by {addr}")
    with globalValues.lock:
        globalValues.readyToPlot = 1  # Set readyToPlot to 1 when connection is established
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        #print("Received:", data)  # Here you would process your angles/distances
        with globalValues.lock:
            globalValues.az, globalValues.el, globalValues.scanLength = map(float, data.split(",")[:3])
            pass
        print(f"Updated values: az={globalValues.az}, el={globalValues.el}, scanLength={globalValues.scanLength}")
        

    conn.close()
    server.close()
    # Define host and port

