import time
import serial
import re

# Open serial port
device = serial.Serial()
device.baudrate = 115200
device.port = "COM11"

try:
    device.open()
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit(1)

i = 0
try:
    while True:
        if device.isOpen():
            i += 1
            try:
                input_data = device.readline()
                s1 = input_data.strip().decode("utf-8")
                
                # Parse latitude and longitude using regular expressions
                match = re.search(r'Location: ([\d.-]+),([\d.-]+)', s1)
                if match:
                    latitude = match.group(1)
                    longitude = match.group(2)
                    
                    # Check if latitude is "600"
                    if latitude != "600":
                        print(f"Latitude: {latitude}, Longitude: {longitude}")
                        
            except UnicodeDecodeError as e:
                print(f"UnicodeDecodeError: {e}")
                print(f"Problematic data: {input_data}")
                
except KeyboardInterrupt:
    print(f"\nexiting program after {i} tests")
    device.close()
    exit(0)
except Exception as e:
    print(f"An error occurred: {e}")
    device.close()
    exit(1)
