import asyncio
import random
import threading
import time

# TODO maybe add a Signal Manager Class that kills and or restarts the signal generator
#
# 


recorded_signals = []
serial_reading = True
lock = threading.Lock()

def kill_signal_generator():
    global serial_reading
    serial_reading = False

# Will be replaced by a function that reads from the serial port
# TODO when receiving from the serial port, poll at 4 * 1600hz
# TODO recorded_signals will be a cache in the future, store the signals in a file (csv)
def signal_generator():
    recorded_signals_local_cache = []
    global serial_reading
    global recorded_signals
    while serial_reading:
        recorded_signals_local_cache.append([
            random.randint(0, 1024), # sensor 1
            random.randint(0, 1024), # sensor 2
            random.randint(0, 1024), # sensor 3
            random.randint(0, 1024), # sensor 4
            random.randint(0, 100), # delay
        ])

        if lock.acquire(False):
            #transfer recorded_signals_local_cache to recorded_signals
            recorded_signals.extend(recorded_signals_local_cache)
            recorded_signals_local_cache = []
            lock.release()

        time.sleep(1/1600)