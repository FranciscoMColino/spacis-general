def pack_sequence(seq):
    # Pack the sequence of integers
    packed_chars = ''.join(chr(num) for num in seq)
     
    return packed_chars
 
def unpack_sequence(packed_chars):
    # Unpack the packed characters to a list of integers
    unpacked_nums = [ord(char) for char in packed_chars]
    
    return unpacked_nums

# Example sequence of integers
seq = [0, 127, 255, 512, 1023, 111,123,123,433,111,34,954]

# Pack the sequence
packed_chars = pack_sequence(seq)
print("Packed chars:", packed_chars, len(str(packed_chars)))

# convert each character to its integer value
packed_vals= [ord(char) for char in packed_chars]
print("Packed chars:", packed_vals, len(str(packed_vals)))


# Unpack the sequence
unpacked_nums = unpack_sequence(packed_chars)
print("Unpacked nums:", unpacked_nums, len(str(unpacked_nums)))