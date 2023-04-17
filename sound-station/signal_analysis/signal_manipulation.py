import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, hilbert


def filter_signal(comp_signal, low_bound, high_bound):

    signal = comp_signal.signal

    # Low pass filter
    cutoff = high_bound
    order = 5
    b, a = butter(order, cutoff / 1000, 'low')
    signal_filtered = filtfilt(b, a, signal)

    # High pass filter
    cutoff = low_bound
    if (cutoff != 0):
        order = 5
        b, a = butter(order, cutoff / 1000, 'high')
        signal_filtered = filtfilt(b, a, signal_filtered)

    return signal_filtered

def default_view(comp_signal):

    signal = comp_signal.signal
    sample_freq = comp_signal.sample_freq
    vmin = comp_signal.vmin
    vmax = comp_signal.vmax

    plt.figure(figsize=(15, 5))
    plt.specgram(signal, Fs=sample_freq, vmin=vmin, vmax=vmax)
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Sample number')
    plt.ylim(0, 100)
    plt.colorbar()

def signal_trim(comp_signal, init_p, end_p):
    if (end_p < init_p): 
        return None
    signal = comp_signal.signal
    return signal[int(len(signal)*init_p):int(len(signal)*end_p)]

# correct offset by making the signal range from -1 to 1 but keeping the the dead zone at 0
def correct_offset(comp_signal):
    #multiply by the elements in the signal 2 and subtract 1
    signal = comp_signal.signal
    return (signal * 2) - np.mean(signal)


"""
This function should isolate the sequence by removing "useless" data points
These data will range from the start of the signal to the start of the sequence and the end of the sequence to the end of the signal
"""
def isolate_single_sequence(comp_signal):

    ### (kinda) WORKING ONLY WHEN THERE IS JUST ONE SEQUENCE

    # How to do this
    # Get the calculated number of useless points, so take_size = len(signal) - squence_size
    # and start by taking equal parts of the end and start with part_size = take_size / 2
    # analyze the variance of each part, the one that presents more variance is more likely to have a subset that belongs to the sequence
    # SO the part with the biggest value gets an adittional take_size / 4 (8, 16 for the next few) and the one with the smallest value gets part_size / 4 taken away
    # repeat this until the difference in variance is at a desired value or for a number of repetitions

    SEQUENCE_SIZE_AT_1600 = 16380
    NUM_REPS = 40 # Maybe tune this value

    signal = comp_signal.signal
    take_size = len(signal) - SEQUENCE_SIZE_AT_1600
    part_size = take_size // 2

    left_size = part_size
    right_size = part_size

    old_lv = -1
    old_rv = -1

    # recheck 
    for _ in range(0, NUM_REPS):

        part_size = part_size // 2

        left = np.array(signal[0:left_size])
        right = np.array(signal[len(signal)-right_size:])
        
        left_variance = np.var(left)
        right_variance = np.var(right)

        if (old_lv == left_variance and old_rv == right_variance): 
            break

        if (left_variance > right_variance):
            left_size -= part_size
            right_size += part_size
        else:   
            left_size += part_size
            right_size -= part_size

        old_lv = left_variance
        old_rv = right_variance
        
    return signal[left_size:len(signal)-right_size]
