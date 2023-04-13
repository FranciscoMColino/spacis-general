def unpack_sequence(packed_chars):
    # Unpack the packed characters to a list of integers
    unpacked_nums = [ord(char) for char in packed_chars]
    
    return unpacked_nums