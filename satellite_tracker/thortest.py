# READ TLEs
# Converts TLEs to usable coordinates
# Display the read TLE in GUI
# Generate GUI
# Show background
# use sofia as base for world map
# display all the 6 keplerians
# display the orbit that was input
# display orbit that is predicted


def read_tle_from_file(file_path):
    """
    Read TLE (Two Line Element) data from a file.
    
    Args:
        file_path (str): Path to the TLE file
        
    Returns:
        list: List of dictionaries containing TLE data for each satellite
              Each dictionary contains 'name', 'line1', and 'line2'
              
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the TLE format is invalid
    """
    satellites = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
        
        # TLE format: name line, followed by two data lines
        if len(lines) % 3 != 0:
            raise ValueError("Invalid TLE file format. Expected groups of 3 lines (name, line1, line2)")
        
        for i in range(0, len(lines), 3):
            satellite_name = lines[i]
            line1 = lines[i + 1]
            line2 = lines[i + 2]
            
            # Basic validation of TLE format
            if not line1.startswith('1 ') or not line2.startswith('2 '):
                raise ValueError(f"Invalid TLE format for satellite {satellite_name}")
            
            if len(line1) != 69 or len(line2) != 69:
                raise ValueError(f"Invalid TLE line length for satellite {satellite_name}")
            
            satellites.append({
                'name': satellite_name,
                'line1': line1,
                'line2': line2
            })
    
    except FileNotFoundError:
        raise FileNotFoundError(f"TLE file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading TLE file: {str(e)}")
    
    return satellites