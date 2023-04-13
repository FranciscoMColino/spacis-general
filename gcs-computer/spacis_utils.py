def unpack_sequence(packed_chars):
    # Unpack the packed characters to a list of integers
    unpacked_nums = [ord(char) for char in packed_chars]
    
    return unpacked_nums

def unpack_sensor_data(data):
    unpacked_data = [unpack_sequence(x) for x in data]
    zipped_data = zip(*unpacked_data)
    return list(zipped_data)