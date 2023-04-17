import numpy as np


def preliminary_pseudorandom_binary_sequence(polynomial_array, generator_resolution):
    cur = pow(2, generator_resolution) - 1
    sequence_size = pow(2, generator_resolution) - 1
    result = np.zeros(sequence_size)
    
    for i in range(0, sequence_size):
        prbs_res = 0

        prbs_res = (cur >> polynomial_array[0])

        for j in range(0, len(polynomial_array) - 1):
            prbs_res ^= (cur >> polynomial_array[j])
        prbs_res &= 1

        cur = (cur << 1) | prbs_res

        array_place = i//32
        element_place = i%32
        result[array_place] |= (prbs_res << element_place)