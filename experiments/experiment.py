import navpy
import numpy as np
from gps_steering import delay_distance_sub_array, ecef_to_ned, lla_to_ecef


def main():

    tx_center_lat, tx_center_lon, tx_center_alt = 41.178219, -8.5951503, 122.9890246
    #balloon_lat, balloon_lon, balloon_alt = 41.1781562, -8.5902002, 127.1203125 # 1
    #balloon_lat, balloon_lon, balloon_alt = 41.18065764298919, -8.591588330168848, 127.1203125 # 2
    balloon_lat, balloon_lon, balloon_alt = 41.18210226618131, -8.589750455485378, 127.1203125 # 3
    #balloon_lat, balloon_lon, balloon_alt = 41.178219, -8.5902002, 127.1203125 # 4

    #tx_center_ecef_x, tx_center_ecef_y, tx_center_ecef_z = lla_to_ecef(tx_center_lat, tx_center_lon, tx_center_alt)
    #balloon_ecef_x, balloon_ecef_y, balloon_ecef_z = lla_to_ecef(balloon_lat, balloon_lon, balloon_alt)
    
    #tx_center_ecef = np.array([tx_center_ecef_x, tx_center_ecef_y, tx_center_ecef_z])
    #balloon_ecef = np.array([balloon_ecef_x, balloon_ecef_y, balloon_ecef_z])
    
    #balloon_ned = ecef_to_ned(balloon_ecef, tx_center_ecef)

    balloon_ned = navpy.lla2ned(balloon_lat, balloon_lon, balloon_alt, tx_center_lat, tx_center_lon, tx_center_alt)
    
    print(balloon_ned, np.linalg.norm(balloon_ned))

    subwoofer_1_ned = np.array([5, -5, 0])

    print(delay_distance_sub_array(balloon_ned, subwoofer_1_ned))

if __name__ == '__main__':
    main()