import os
import matplotlib.pyplot as plt
import osmnx as ox
import matplotlib.image as mpimg
import numpy as np
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

# Get the street network for Blacksburg, VA
graph = ox.graph_from_address('495 Old Turner St, Blacksburg, VA 24060', dist=500, dist_type='bbox')

# Create a figure and axis
plt.ion()
fig, ax = ox.plot_graph(graph, show=False, close=False)

# Load the icon image
icon = mpimg.imread(r'C:\Users\abrah\Downloads\icon (1).png')

# Display the icon at a specific location on the map
icon_extent = 0.00025  # Adjust icon size
lat, lon = 37.139, -80.256  # Initial position (replace with your desired coordinates)

# Calculate the icon extent coordinates based on initial position
icon_extent_coords = [lon - icon_extent, lon + icon_extent, lat - icon_extent, lat + icon_extent]
icon_plot = ax.imshow(icon, extent=icon_extent_coords, zorder=10)

i = 0
try:
    while True:
        i += 1
        
        if device.isOpen():
            try:
                input_data = device.readline()
                s1 = input_data.strip().decode("utf-8")
                
                # Parse latitude and longitude using regular expressions
                match = re.search(r'Location: ([\d.-]+),([\d.-]+)', s1)
                if match:
                    latitude = float(match.group(1))
                    longitude = float(match.group(2))
                    
                    # Check if latitude is "600"
                    if latitude != 600.0:
                        print(f"Latitude: {latitude}, Longitude: {longitude}")
                        
                        # Update icon position
                        icon_extent_coords = [longitude - icon_extent, longitude + icon_extent, latitude - icon_extent, latitude + icon_extent]
                        
                        # Update icon plot extent
                        icon_plot.set_extent(icon_extent_coords)
                        icon_plot.set_data(icon)
                        
                        plt.draw()
                        plt.pause(0.5)
                        
            except UnicodeDecodeError as e:
                print(f"UnicodeDecodeError: {e}")
                print(f"Problematic data: {input_data}")
                
except KeyboardInterrupt:
    print(f"\nexiting program after {i} tests")
    device.close()
    plt.close()
    exit(0)
except Exception as e:
    print(f"An error occurred: {e}")
    device.close()
    plt.close()
    exit(1)
