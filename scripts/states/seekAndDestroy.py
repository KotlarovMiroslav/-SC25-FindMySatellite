from utils import set_angle
from globalsConfig import *
from main import *

def seekAndDestroy():
    global passedStep, lock, curDeg, searching, dataOutput, poi, globalReading
    #samePoiCounter = 0
    #if (poi == lastPoi):
        #if(samePoiCounter == 3):
            #with lock:
                #searching = 1
                #pass
        #samePoiCounter = samePoiCounter + 1
    while True:
        if searching == 0:
            print(f"TRACKING POI around {poi*5}°")
            #lastPoi = poi)
            
            min_deg = max((poi * 5) -15, 0)
            max_deg = min((poi * 5) +15, 60)
            degree = max_deg + 1
            for degree in range(max_deg + 1, min_deg, -5):
                with lock:
                    while passedStep != 0:
                        pass
                set_angle(degree)
                curDeg = degree
                #time.sleep(0.1)
                with lock:
                    passedStep = 1
                    pass
                time.sleep(0.06)
            min_deg = max((poi * 5) -15, 0)
            max_deg = min((poi * 5) +15, 60)
            for degree in range(min_deg, max_deg + 1, 5):
                with lock:
                    while passedStep != 0:
                        pass
                set_angle(degree)
                curDeg = degree
                #time.sleep(0.1)
                with lock:
                    passedStep = 1
                    pass
                time.sleep(0.06)
            
            min_deg = max((poi * 5) -15, 0)
            max_deg = min((poi * 5) +15, 60)
            
            #samePoiCounter = samePoiCounter + 1
            #if samePoiCounter == 5:
                #with lock:
                    #searching = 1
                    #samePoiCounter = 0
                    #pass
            min_poi = max(poi - 3, 2)
            max_poi = min(poi + 2, len(dataOutput) - 2)
            baseline = dataOutput[curPos]
            diff = abs(globalReading - baseline)
            if diff > 100:
                print(f"Scan:{globalReading},Base: {baseline} ,Diff:{diff}")
                poi = curPos
                print(f"POI SHIFTED — New center: {poi*5}°")
                curPos += 1
            if curPos > max_poi:
                curPos = min_poi