import sequence_generation as sg

    ##
    #    Sequences:
    #        0 - 12,  8, 5, 1
    #        1 - 12, 10, 8, 7, 4, 1
    #        2 - 12, 11, 8, 5, 4, 2
    #        3 - 12, 10, 9, 3
    ##

def main():

    polynomial_array_0 = [12, 8, 5, 1]
    polynomial_array_1 = [12, 10, 8, 7, 4, 1]
    polynomial_array_2 = [12, 11, 8, 5, 4, 2]
    polynomial_array_3 = [12, 10, 9, 3]

    preliminary_sequence_0 = sg.preliminary_pseudorandom_binary_sequence(polynomial_array_0, 12)
    transformed_sequence_0 = sg.transform_sequence(preliminary_sequence_0, 12)

    # open csv file to write to
    with open('sequence_0.csv', 'w') as f:
        for i in range(0, 128):
            for j in range(0, 32):
                #f.write(f'{transformed_sequence_0[i] >> j & 1}\n')
                continue

    return 0

main()