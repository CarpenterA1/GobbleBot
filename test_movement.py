import os
import matplotlib.pyplot as plt
import osmnx as ox
import matplotlib.image as mpimg
import numpy as np

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

x_min, x_max = -80.42916, -80.41747
y_min, y_max = 37.22507, 37.23440

i = 0
try:
    while True:
        i += 1
        
        # Simulate latitude and longitude for testing within the given bounds
        latitude = np.random.uniform(y_min, y_max)  # Random latitude between y_min and y_max
        longitude = np.random.uniform(x_min, x_max)  # Random longitude between x_min and x_max
        
        print(f"Latitude: {latitude}, Longitude: {longitude}")
        
        # Update icon position
        icon_extent_coords = [longitude - icon_extent, longitude + icon_extent, latitude - icon_extent, latitude + icon_extent]
        icon_plot.set_extent(icon_extent_coords)
        
        plt.draw()
        plt.pause(0.5)
                
except KeyboardInterrupt:
    print(f"\nexiting program after {i} tests")
    plt.close()
    exit(0)
except Exception as e:
    print(f"An error occurred: {e}")
    plt.close()
    exit(1)
