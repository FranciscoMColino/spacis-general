import math

import numpy as np
from geopy.distance import great_circle


def lla_to_ecef(latitude, longitude, altitude):
    # WGS84 ellipsoidal parameters
    a = 6378137.0  # Equatorial radius in meters
    f = 1 / 298.257223563  # Flattening factor

    # Calculate derived parameters
    b = (1 - f) * a
    e_sq = 1 - (b ** 2) / (a ** 2)
    N = a / math.sqrt(1 - e_sq * math.sin(math.radians(latitude)) ** 2)

    # Convert to ECEF coordinates
    x = (N + altitude) * math.cos(math.radians(latitude)) * math.cos(math.radians(longitude))
    y = (N + altitude) * math.cos(math.radians(latitude)) * math.sin(math.radians(longitude))
    z = ((b ** 2 / a ** 2) * N + altitude) * math.sin(math.radians(latitude))

    return x, y, z

def ecef_to_ned(ecef_point, reference_ecef):
    dx = ecef_point[0] - reference_ecef[0]
    dy = ecef_point[1] - reference_ecef[1]
    dz = ecef_point[2] - reference_ecef[2]

    rotation_matrix = np.array([
        [-np.sin(reference_ecef[0]),                                np.cos(reference_ecef[0]),                                  0],
        [-np.sin(reference_ecef[1]) * np.cos(reference_ecef[0]),    -np.sin(reference_ecef[1]) * np.sin(reference_ecef[0]),     np.cos(reference_ecef[1])],
        [np.cos(reference_ecef[1]) * np.cos(reference_ecef[0]),     np.cos(reference_ecef[1]) * np.sin(reference_ecef[0]),      np.sin(reference_ecef[1])]
    ])

    ned_point = np.dot(rotation_matrix, np.array([dx, dy, dz]))

    return ned_point


def delay_distance_sub_array(balloon_ned_pos, subwoofer_ned_pos):
    direction_versor = balloon_ned_pos / np.linalg.norm(balloon_ned_pos)
    delay_distance = np.dot( subwoofer_ned_pos, direction_versor)
    return delay_distance