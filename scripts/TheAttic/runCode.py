from abc import ABC, abstractmethod
def seekAndDestroy():
    global passedStep, lock, curDeg, searching, dataOutput, poi

    direction = -1  # Start scanning down
    degree = 0

    while True:
        if searching == 0:
            with lock:
                current_poi = poi

            # Continuously update center and bounds
            center_deg = current_poi * 5
            min_deg = (max(center_deg - 40, 0) // 5) * 5
            max_deg = (min(center_deg + 40, 60) // 5) * 5

            # Update scanning direction when hitting bounds
            if direction == -1 and degree <= min_deg:
                direction = 1  # switch to upward
            elif direction == 1 and degree >= max_deg:
                direction = -1  # switch to downward

            # Move servo
            with lock:
                while passedStep != 0:
                    pass
            set_angle(degree)
            curDeg = degree
            with lock:
                passedStep = 1
            time.sleep(0.06)

            # Recalculate POI for next pass
            with lock:
                updated_poi = poi

            # Adjust tracking center if it shifted
            if updated_poi != current_poi:
                print(f"[S&D] New POI @ {updated_poi * 5}° → Re-centering scan")
                center_deg = updated_poi * 5
                min_deg = (max(center_deg - 40, 0) // 5) * 5
                max_deg = (min(center_deg + 40, 60) // 5) * 5
                # reset scan position
                degree = center_deg
                direction = -1 if degree > max_deg else 1

            # Continue scan step
            degree += 5 * direction


