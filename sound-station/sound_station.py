import matplotlib.pyplot as plt
import sequence_generation as sg
import signals.signal_manipulation as signal_manipulation
from signals.captured_signal import CapturedSignal
from signals.single_sequence import SingleGenaratedSequence

    ##
    #    Sequences:
    #        0 - 12,  8, 5, 1
    #        1 - 12, 10, 8, 7, 4, 1
    #        2 - 12, 11, 8, 5, 4, 2
    #        3 - 12, 10, 9, 3
    ##

def sequence_gen():

    polynomial_array_0 = [12, 8, 5, 1]
    polynomial_array_1 = [12, 10, 8, 7, 4, 1]
    polynomial_array_2 = [12, 11, 8, 5, 4, 2]
    polynomial_array_3 = [12, 10, 9, 3]

    preliminary_sequence_0 = sg.preliminary_pseudorandom_binary_sequence(polynomial_array_0, 12)
    preliminary_sequence_1 = sg.preliminary_pseudorandom_binary_sequence(polynomial_array_1, 12)
    preliminary_sequence_2 = sg.preliminary_pseudorandom_binary_sequence(polynomial_array_2, 12)
    preliminary_sequence_3 = sg.preliminary_pseudorandom_binary_sequence(polynomial_array_3, 12)

    transformed_sequence_0 = sg.transform_sequence(preliminary_sequence_0, 12)
    transformed_sequence_1 = sg.transform_sequence(preliminary_sequence_1, 12)
    transformed_sequence_2 = sg.transform_sequence(preliminary_sequence_2, 12)
    transformed_sequence_3 = sg.transform_sequence(preliminary_sequence_3, 12)

    # open csv file to write to
    with open('data/new_gens/sequence_0.csv', 'w') as f:
        f.write('values\n')
        for i in range(0, 128):
            for j in range(0, 32):
                f.write(f'{transformed_sequence_0[i] >> j & 1}\n')
                continue

    with open('data/new_gens/sequence_1.csv', 'w') as f:
        f.write('values\n')
        for i in range(0, 128):
            for j in range(0, 32):
                f.write(f'{transformed_sequence_1[i] >> j & 1}\n')
                continue
    
    with open('data/new_gens/sequence_2.csv', 'w') as f:
        f.write('values\n')
        for i in range(0, 128):
            for j in range(0, 32):
                f.write(f'{transformed_sequence_2[i] >> j & 1}\n')
                continue
    
    with open('data/new_gens/sequence_3.csv', 'w') as f:
        f.write('values\n')
        for i in range(0, 128):
            for j in range(0, 32):
                f.write(f'{transformed_sequence_3[i] >> j & 1}\n')
                continue

    return 0

def sequence_viz():
    old_seq = SingleGenaratedSequence('./data/old_gens_fix/sequence_1.csv')
    old_seq.signal = signal_manipulation.filter_signal(old_seq, 10, 50)
    signal_manipulation.default_view(old_seq)

    new_seq = SingleGenaratedSequence('./data/new_gens/sequence_1.csv')
    new_seq.signal = signal_manipulation.filter_signal(new_seq, 10, 50)
    signal_manipulation.default_view(new_seq)
    plt.show()

def capture_viz():
    capture_seq = CapturedSignal('./data/captures/records_11.csv')
    #capture_seq.signal = signal_manipulation.correct_offset(capture_seq)
    capture_seq.signal = signal_manipulation.filter_signal(capture_seq, 10, 50)

    sequence_sig_1 = signal_manipulation.signal_trim(capture_seq, 0.0, 0.13)
    sequence_sig_2 = signal_manipulation.signal_trim(capture_seq, 0.14, 0.28)
    sequence_sig_3 = signal_manipulation.signal_trim(capture_seq, 0.27, 0.42)
    sequence_sig_4 = signal_manipulation.signal_trim(capture_seq, 0.42, 0.56)
    sequence_sig_5 = signal_manipulation.signal_trim(capture_seq, 0.58, 0.70)
    sequence_sig_6 = signal_manipulation.signal_trim(capture_seq, 0.70, 0.84)
    sequence_sig_7 = signal_manipulation.signal_trim(capture_seq, 0.86, 0.99)

    sequence_signals = [sequence_sig_1, sequence_sig_2, sequence_sig_3, sequence_sig_4, sequence_sig_5, sequence_sig_6, sequence_sig_7]

    for i in range(0, 7):
        capture_seq.signal = sequence_signals[i]
        signal_manipulation.default_view(capture_seq)

    plt.show()

## Main

capture_viz()