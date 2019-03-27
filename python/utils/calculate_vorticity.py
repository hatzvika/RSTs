import numpy as np
import math


# Calculate Geostrophic vorticity
def calculate_vorticity(uwind_data, vwind_data, resolution, lats, total_lat, total_lon):
    vorticity_map = np.zeros((total_lat, total_lon))
    dy = 2 * resolution * 111000  # 111 Km. is the distance of 1 degree latitude. We look for the distance between 2 points.
    for current_lat in range(1, total_lat-1):
        for current_lon in range(1, total_lon-1):
            duwind = uwind_data[current_lat, current_lon + 1] - uwind_data[current_lat, current_lon - 1]
            dvwind = vwind_data[current_lat + 1, current_lon] - vwind_data[current_lat - 1, current_lon]
            dx = dy * math.cos(math.radians(lats[current_lat]))
            vorticity_map[current_lat, current_lon] = (dvwind/dx) - (duwind/dy)

    return vorticity_map
