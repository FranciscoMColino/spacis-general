import sequence_generation as sg


def main():
    polynomial_array_0 = [12, 8, 5, 1]

    preliminary_sequence_0 = sg.preliminary_pseudorandom_binary_sequence(polynomial_array_0, 12)

    sequence_0 = sg.transform_sequence(preliminary_sequence_0, 12)

    for i in range(0, len(sequence_0)):
        print(hex(sequence_0[i]))

            
    

if __name__ == '__main__':
    main()