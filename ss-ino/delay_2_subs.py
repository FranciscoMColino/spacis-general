import sys

import numpy as np

if __name__ == "__main__":
    # first arg is subwoofer distance, second is number of delayed cycles
    if len(sys.argv) < 3:
        print("Usage: python delay_2_subs.py <sub_distance> <delay_cycles>")
        sys.exit()

    sub_distance = float(sys.argv[1])
    delay_cycles = float(sys.argv[2])

    # speed of sound in air
    c = 343.0
    delay_between_tx = 1/1600 # in seconds
    distance_traveled = c * delay_between_tx * delay_cycles

    print("Distance traveled: {} meters".format(distance_traveled))

    transmission_angle = np.rad2deg(np.arctan(distance_traveled/sub_distance))

    print("Transmission angle: {} degrees".format(transmission_angle))
    