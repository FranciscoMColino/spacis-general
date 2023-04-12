import base64


def pack_sequence(sequence):
    packed_data = bytearray()
    bit_position = 0
    current_byte = 0
    for num in sequence:
        current_byte |= num << bit_position
        bit_position += 10
        while bit_position >= 8:
            packed_data.append(current_byte & 0xFF)
            current_byte >>= 8
            bit_position -= 8
    if bit_position > 0:
        packed_data.append(current_byte & 0xFF)
    return packed_data

def unpack_sequence(compressed_string):
    unpacked_data = compressed_string
    sequence = []
    bit_position = 0
    current_num = 0
    for byte in unpacked_data:
        current_num |= (byte & 0xFF) << bit_position
        bit_position += 8
        while bit_position >= 10:
            sequence.append(current_num & 0x3FF)
            current_num >>= 10
            bit_position -= 10
    if bit_position > 0:
        sequence.append(current_num & 0x3FF)
    return sequence

# Original sequence
original_sequence = [0, 127, 255, 512, 1023, 111,123,123,433,111,34,954]

# Pack the sequence into a compressed string
compressed_string = pack_sequence(original_sequence)

# Unpack the compressed string into a sequence
unpacked_sequence = unpack_sequence(compressed_string)

print("Original Sequence:", original_sequence, )
print("Packed Data:", compressed_string, len(compressed_string))
print("Unpacked Sequence:", unpacked_sequence)
