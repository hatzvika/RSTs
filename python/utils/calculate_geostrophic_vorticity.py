import numpy as np
import math


# Calculate Geostrophic vorticity
def calculate_geostrophic_vorticity(slp_data, resolution, lats, total_lat, total_lon):
    ugwind_map = np.zeros((total_lat, total_lon))
    vgwind_map = np.zeros((total_lat, total_lon))
    geostrophic_vorticity_map = np.zeros((total_lat, total_lon))
    rho = 1.2754
    omega = 7.27e-5
    dy = 2 * resolution * 111000  # 111 Km. is the distance of 1 degree latitude. We look for the distance between 2 points.
    for current_lat in range(1, total_lat - 1):
        for current_lon in range(1, total_lon - 1):
            dpx = slp_data[current_lat, current_lon + 1] - slp_data[current_lat, current_lon - 1]
            dpy = slp_data[current_lat + 1, current_lon] - slp_data[current_lat - 1, current_lon]
            dx = dy * math.cos(math.radians(lats[current_lat]))
            ugwind_map[current_lat, current_lon] = (((-1) / rho) * (dpy / dy)) / (2 * omega * math.sin(math.radians(current_lat)))
            vgwind_map[current_lat, current_lon] = (((1) / rho) * (dpx / dx)) / (2 * omega * math.sin(math.radians(current_lat)))

    for current_lat in range(2, total_lat - 1):
        for current_lon in range(2, total_lon - 1):
            duwind = ugwind_map[current_lat + 1, current_lon] - ugwind_map[current_lat - 1, current_lon]
            dvwind = vgwind_map[current_lat, current_lon + 1] - vgwind_map[current_lat, current_lon - 1]
            geostrophic_vorticity_map[current_lat, current_lon] = (dvwind / dx) - (duwind / dy)

    return geostrophic_vorticity_map

