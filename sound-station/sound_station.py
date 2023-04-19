import math

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal
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

def sequence_plot():
    polynomial_array_0 = [12, 8, 5, 1]
    preliminary_sequence_0 = sg.preliminary_pseudorandom_binary_sequence(polynomial_array_0, 12)
    pre_corr_sequence_0 = sg.pre_corr_processing(preliminary_sequence_0, 12)

    plt.plot(pre_corr_sequence_0)
    plt.show()

def correlation_capture():
    capture_seq = CapturedSignal('./data/captures/records_11.csv')
    #capture_seq.signal = signal_manipulation.correct_offset(capture_seq)
    #capture_seq.signal = signal_manipulation.filter_signal(capture_seq, 10, 50)

    sequence_sig_1 = signal_manipulation.signal_trim(capture_seq, 0.0, 0.13)
    sequence_sig_2 = signal_manipulation.signal_trim(capture_seq, 0.14, 0.28)
    sequence_sig_3 = signal_manipulation.signal_trim(capture_seq, 0.27, 0.42)
    sequence_sig_4 = signal_manipulation.signal_trim(capture_seq, 0.42, 0.56)
    sequence_sig_5 = signal_manipulation.signal_trim(capture_seq, 0.58, 0.70)
    sequence_sig_6 = signal_manipulation.signal_trim(capture_seq, 0.70, 0.84)
    sequence_sig_7 = signal_manipulation.signal_trim(capture_seq, 0.86, 0.99)

    sequence_sigs = [sequence_sig_1, sequence_sig_2, sequence_sig_3, sequence_sig_4, sequence_sig_5, sequence_sig_6, sequence_sig_7]

    polynomial_array_0 = [12, 8, 5, 1]
    polynomial_array_1 = [12, 10, 8, 7, 4, 1]
    polynomial_array_2 = [12, 11, 8, 5, 4, 2]
    polynomial_array_3 = [12, 10, 9, 3]

    polynomial_array = polynomial_array_3
    preliminary_sequence = sg.preliminary_pseudorandom_binary_sequence(polynomial_array, 12)
    pre_corr_sequence = sg.pre_corr_processing(preliminary_sequence, 12)
    signal_i, signal_g = pre_corr_sequence

    fx, ax = plt.subplots(len(sequence_sigs), 3, figsize=(10, 10))


    # do for all sequences
    for i in range(0, len(sequence_sigs)):
        capture_seq.signal = sequence_sigs[i]

        corr_i = np.correlate(capture_seq.signal, signal_i, 'full')
        corr_g = np.correlate(capture_seq.signal, signal_g, 'full')
        corr_x = np.sqrt(np.power(corr_i, 2) + np.power(corr_g, 2))

        ax[i][0].plot(corr_i)
        ax[i][1].plot(corr_g)
        ax[i][2].plot(corr_x)
        
    plt.show()

def correlate_1_capture_all_gen():
    capture_seq = CapturedSignal('./data/captures/records_11.csv')
    #capture_seq.signal = signal_manipulation.correct_offset(capture_seq)
    #capture_seq.signal = signal_manipulation.filter_signal(capture_seq, 10, 50)

    sequence_sig_1 = signal_manipulation.signal_trim(capture_seq, 0.0, 0.13)
    sequence_sig_2 = signal_manipulation.signal_trim(capture_seq, 0.14, 0.28)
    sequence_sig_3 = signal_manipulation.signal_trim(capture_seq, 0.27, 0.42)
    sequence_sig_4 = signal_manipulation.signal_trim(capture_seq, 0.42, 0.56)
    sequence_sig_5 = signal_manipulation.signal_trim(capture_seq, 0.58, 0.70)
    sequence_sig_6 = signal_manipulation.signal_trim(capture_seq, 0.70, 0.84)
    sequence_sig_7 = signal_manipulation.signal_trim(capture_seq, 0.86, 0.99)

    capture_seq.signal = sequence_sig_3

    polynomial_array_0 = [12, 8, 5, 1]
    polynomial_array_1 = [12, 10, 8, 7, 4, 1]
    polynomial_array_2 = [12, 11, 8, 5, 4, 2]
    polynomial_array_3 = [12, 10, 9, 3]

    polynomial_arrays = [polynomial_array_0, polynomial_array_1, polynomial_array_2, polynomial_array_3]

    fx, ax = plt.subplots(len(polynomial_arrays), 3, figsize=(10, 10))
    for i in range(0, len(polynomial_arrays)):
        polynomial_array = polynomial_arrays[i]
        preliminary_sequence = sg.preliminary_pseudorandom_binary_sequence(polynomial_array, 12)
        pre_corr_sequence = sg.pre_corr_processing(preliminary_sequence, 12)
        signal_i, signal_g = pre_corr_sequence

        corr_i = np.correlate(a=capture_seq.signal, v=signal_i)
        corr_i /= (len(capture_seq.signal) * np.std(capture_seq.signal) * np.std(signal_i))
        corr_g = np.correlate(a=capture_seq.signal, v=signal_g)
        corr_g /= (len(capture_seq.signal) * np.std(capture_seq.signal) * np.std(signal_g))
        corr_x = np.sqrt(np.power(corr_i, 2) + np.power(corr_g, 2))

        ax[i][0].plot(corr_i)
        ax[i][1].plot(corr_g)
        ax[i][2].plot(corr_x)

    plt.show()

def correlate_gen_with_treament():
    new_seq = SingleGenaratedSequence('./data/new_gens/sequence_0.csv')
    new_seq.signal = signal_manipulation.filter_signal(new_seq, 10, 50)

    polynomial_array_0 = [12, 8, 5, 1]
    polynomial_array_1 = [12, 10, 8, 7, 4, 1]
    polynomial_array_2 = [12, 11, 8, 5, 4, 2]
    polynomial_array_3 = [12, 10, 9, 3]

    polynomial_array = polynomial_array_1
    preliminary_sequence = sg.preliminary_pseudorandom_binary_sequence(polynomial_array, 12)
    pre_corr_sequence = sg.pre_corr_processing(preliminary_sequence, 12)
    signal_i, signal_g = pre_corr_sequence

    corr_i = np.correlate(new_seq.signal, signal_i, 'full')
    corr_g = np.correlate(new_seq.signal, signal_g, 'full')
    corr_x = np.sqrt(np.power(corr_i, 2) + np.power(corr_g, 2))

    fx, ax = plt.subplots(1, 3, figsize=(10, 5))
    ax[0].plot(corr_i)
    ax[1].plot(corr_g)
    ax[2].plot(corr_x)

    plt.show()

def correlate_full_capture():
    capture_seq = CapturedSignal('./data/captures/records_11.csv')
    #capture_seq.signal = signal_manipulation.correct_offset(capture_seq)
    capture_seq.signal = signal_manipulation.filter_signal(capture_seq, 10, 50)

    polynomial_array_0 = [12, 8, 5, 1]
    polynomial_array_1 = [12, 10, 8, 7, 4, 1]
    polynomial_array_2 = [12, 11, 8, 5, 4, 2]
    polynomial_array_3 = [12, 10, 9, 3]

    polynomial_arrays = [polynomial_array_0, polynomial_array_1, polynomial_array_2, polynomial_array_3]

    fx, ax = plt.subplots(len(polynomial_arrays), 3, figsize=(10, 10))
    for i in range(0, len(polynomial_arrays)):
        polynomial_array = polynomial_arrays[i]
        preliminary_sequence = sg.preliminary_pseudorandom_binary_sequence(polynomial_array, 12)
        pre_corr_sequence = sg.pre_corr_processing(preliminary_sequence, 12)
        signal_i, signal_g = pre_corr_sequence

        corr_i = np.correlate(a=capture_seq.signal, v=signal_i)
        corr_i /= (len(capture_seq.signal) * np.std(capture_seq.signal) * np.std(signal_i))
        corr_g = np.correlate(capture_seq.signal, signal_g)
        corr_g /= (len(capture_seq.signal) * np.std(capture_seq.signal) * np.std(signal_g))
        corr_x = np.sqrt(np.power(corr_i, 2) + np.power(corr_g, 2))
        corr_x = np.power(corr_x, 3)

        ax[i][0].plot(corr_i)
        ax[i][1].plot(corr_g)
        ax[i][2].plot(corr_x)
    plt.show()

## Main

correlate_full_capture()