import threading
from time import sleep
from time import time
import sys
import os
import stepper
import RPi.GPIO as GPIO
import globalsConfig as gv
from utils import lidar_reader
from utils import set_angle
#from piConnection import pi_connection
#CONFIGURATION
size_of_array = 9
sleep(3) # Wait for the GPIO to initialize properly

sys.path.append(os.path.dirname(os.path.abspath(__file__))) #remove "#"from the begining before flight

# t_piCon = threading.Thread(target=pi_connection, daemon=True)
# t_piCon.start()
t_lidar = threading.Thread(target=lidar_reader, daemon=True)
t_lidar.start()
# while not gv.ready_state:
#     print("Waiting for connection to laptop...")
#     sleep(0.5)

stepper.setup_stepper()
i = 0
notScannedEnv = 1
readings = [[0 for x in range(size_of_array)] for y in range(7)] 
curIteration = 0

set_angle(185)
gv.servo_pos = 0
sleep(0.5)
while notScannedEnv:   #SCAN ENV
    #print(gv.latest_distance)
    #sleep(1)
    
    if( i == 7):
        stepper.stepper(-180)
        gv.stepper_pos += -180
        i = 0# Move stepper back to 0 position
        notScannedEnv = 0

    else:
        for curAngle in range (0, size_of_array):
            set_angle(100 + curAngle * 90/size_of_array)
            gv.servo_pos += curAngle * 90/size_of_array
            sleep(0.2)
            readings[curIteration][curAngle] = gv.latest_distance
            #print("Readings: ", readings)
        i += 1  # Initialize stepper position to 0
        if( i == 7):
            continue
        stepper.stepper(30)
        gv.stepper_pos += 30
        curIteration += 1
        sleep(0.2) 



i = 0
droneNotFound = 1
curIteration = 0
curTime = time()
while notScannedEnv == 0: # COMPARE ENV
    #print(gv.latest_distance)
    sleep(0.2)
    
    if( i == 7):
        print("GG")
        stepper.stepper(-189)
        gv.stepper_pos -= 189
        sleep(1)
        GPIO.cleanup()
        for curPos in gv.det_pos:
            print(curPos)
        sys.exit(0)
    else:
        while droneNotFound:
            print(f"Current Iteration: {curIteration}, Readings: {readings[curIteration]}")
            print("curAngle: ", curAngle)
            for curAngle in range (0, size_of_array):
                if(curAngle == 0):
                    set_angle(100 + curAngle * 90/size_of_array)
                    gv.servo_pos = curAngle * 90/size_of_array
                    sleep(0.07)
                else:
                    set_angle(100 + curAngle * 90/size_of_array)
                    gv.servo_pos = curAngle * 90/size_of_array
                    sleep(0.05)
                
                #print(curIteration, ":curIteration  curAngle:" ,curAngle, "read: ", gv.latest_distance)
                #print(abs(gv.latest_distance - readings[curIteration][curAngle]))
                if(abs(gv.latest_distance - readings[curIteration][curAngle]) > 70 and abs(gv.latest_distance - readings[curIteration][curAngle]) < 60000 and gv.latest_distance < 350):
                    print("Object Spotted at angle: ", curAngle*17)
                    print("curAngle: ", curAngle,"curIteration:", curIteration ,"compared to readings: ", readings[curIteration][curAngle])
                    droneNotFound = 0
                    with gv.lock:
                        gv.target_found = 1
                        pass
                    gv.det_pos.append([gv.stepper_pos, gv.servo_pos,gv.latest_distance, round(time() - curTime,2)])
                    break

            if droneNotFound == 0:
                break
            
            for curAngle in range (size_of_array-1, -1,-1):
                if(curAngle == 0):
                    set_angle(100 + curAngle * 90/size_of_array)
                    gv.servo_pos = curAngle * 90/size_of_array
                    sleep(0.07)
                else:
                    set_angle(100 + curAngle * 90/size_of_array)
                    gv.servo_pos = curAngle * 90/size_of_array
                    sleep(0.05)
                #print(abs(gv.latest_distance - readings[curIteration][curAngle]))
                if(abs(gv.latest_distance - readings[curIteration][curAngle]) > 70 and abs(gv.latest_distance - readings[curIteration][curAngle]) < 60000 and gv.latest_distance < 350):
                    print("Object Spotted at angle: ", curAngle*17)
                    droneNotFound = 0
                    with gv.lock:
                        gv.target_found = 1
                        pass
                    gv.det_pos.append([gv.stepper_pos, gv.servo_pos,gv.latest_distance, round(time() - curTime,2)])
                    break
            
        i += 1 
        set_angle(185)
        gv.servo_pos = 0
        stepper.stepper(30)
        gv.stepper_pos += 30
        print("Drone Found")
        droneNotFound = 1
        curIteration += 1
        
