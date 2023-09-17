import os

import yaml


def unpack_sequence(packed_chars):
    # Unpack the packed characters to a list of integers

    unpacked_nums = [ord(char) for char in packed_chars]
    return unpacked_nums


def unpack_sensor_data(data):
    unpacked_data = [unpack_sequence(x) for x in data]
    zipped_data = zip(*unpacked_data)
    return list(zipped_data)


def fromhex(hex_str, nbits=32):
    # Convert the hex string to an integer
    try:
        val = int(hex_str, 16)

        # If the most significant bit is set, subtract 2^nbits to get the original signed integer
        if val >= 2**(nbits - 1):
            val -= 2**nbits
    except Exception as e:
        print('Error converting hex to int: {}'.format(e))
        val = 0

    return val


def unpack_elapsed_time(data):
    elapsed_time = data.split(',')
    elapsed_time = [fromhex(x) for x in elapsed_time]
    return elapsed_time


def unpack_pps_ids(data):
    try:
        pps_ids = data.split(',')
        pps_ids = [int(x) for x in pps_ids]
    except Exception as e:
        print('Error unpacking pps ids: {}'.format(e, pps_ids))
        pps_ids = []
    return pps_ids


def parse_settings(filename='./settings.yaml'):

    if not os.path.exists(filename):
        print('File does not exist:', filename)
        quit()

    print('Using for settings: ', filename)

    with open(filename) as f:
        return yaml.safe_load(f)
