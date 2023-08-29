import math


def calculate_ned_position(sub):
    # reference_ned_center = [0, 0, 0]
    tangent = math.sqrt(sub["raw_pos_data"]["distance"]**2 - sub["raw_pos_data"]["height"]**2)
    sub["ned_pos"][0] = tangent * math.cos(math.radians(sub["raw_pos_data"]["orientation"]))
    sub["ned_pos"][1] = tangent * math.sin(math.radians(sub["raw_pos_data"]["orientation"]))
    sub["ned_pos"][2] = -sub["raw_pos_data"]["height"]
    return sub["ned_pos"]

def calculate_ned_positions(subwoofer_array):

    for i in range(1, len(subwoofer_array)):
        sub = subwoofer_array["sub{}".format(i)]
        sub["ned_pos"] = calculate_ned_position(sub)