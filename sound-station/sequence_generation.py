import math

import numpy as np


def preliminary_pseudorandom_binary_sequence(polynomial_array, generator_resolution):
    cur = pow(2, generator_resolution) - 1
    sequence_size = pow(2, generator_resolution) - 1
    result = np.zeros(math.ceil(sequence_size/32), dtype=np.uint32)
    
    for i in range(0, sequence_size):

        prbs_res = (cur >> polynomial_array[0])

        for j in range(1, len(polynomial_array)):
            prbs_res ^= (cur >> polynomial_array[j])
        prbs_res &= 1

        cur = (cur << 1) | prbs_res

        array_place = math.floor(i/32)
        element_place = i%32

        result[array_place] |= (prbs_res << element_place)

    return result

def transform_sequence(preliminary_sequence, sequence_resolution):
    sequence_size = pow(2, sequence_resolution) - 1
    ps_size = math.ceil(sequence_size/32)
    
    acc = 0
    array_place = 0
    element_place = 0
    bit = 0
    new_bit = 0

    result = np.zeros(ps_size, dtype=np.uint32)

    for i in range(0, sequence_size):
        array_place = math.floor(i/32)
        element_place = i%32
        bit = ((preliminary_sequence[array_place] >> element_place) & 1) << element_place
        acc += 3 if bit else 1
        new_bit = (acc//16) % 2
        result[array_place] &= ~(1 << element_place)
        result[array_place] |= (new_bit << element_place)

    return result