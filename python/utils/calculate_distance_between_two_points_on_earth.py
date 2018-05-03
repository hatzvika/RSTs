from math import sin, cos, sqrt, atan2, radians


def calculate_distance_between_two_points_on_earth(lat1_degrees, lon1_degrees, lat2_degrees, lon2_degrees):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1_degrees)
    lon1 = radians(lon1_degrees)
    lat2 = radians(lat2_degrees)
    lon2 = radians(lon2_degrees)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance