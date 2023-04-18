import threading
import time

import serial.tools.list_ports


def test():
    # List all available serial ports
    ports = serial.tools.list_ports.comports()

    # Filter the list to find the port with "Arduino" in its description
    arduino_ports = [
        p.device
        for p in serial.tools.list_ports.comports()
        if 'Arduino' in p.description
    ]

    ser  = serial.Serial(arduino_ports[0], 500000)

    # Read and print incoming messages from the Arduino
    while True:
        if ser.in_waiting > 0:
            messages = []
            while ser.in_waiting > 0:
                messages.append(ser.readline().decode('utf-8').rstrip())
            print(len(messages))

recorded_signals = []
serial_reading = True
lock = threading.Lock()

def kill_signal_generator():
    global serial_reading
    serial_reading = False

class GRPISerial():
    def __init__(self):
        self.baundrate = 500000
        self.data = []
    
    def connect(self):
        # Filter the list to find the port with "Arduino" in its description
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' in p.description
        ]

        self.ser  = serial.Serial(arduino_ports[0], self.baundrate)
        
        if self.ser:
            print("Connected successfully to the arduino", arduino_ports[0])
            return True
        else:
            print("Failed to connect to the arduino")
            return False

    def read_messages(self):

        ser = self.ser
        recorded_signals_local_cache = []
        global serial_reading
        global recorded_signals

        while serial_reading:
            
            while ser.in_waiting > 0:
                msg = ser.readline().decode('utf-8').rstrip().split(',')
                try:
                    msg = [int(i) for i in msg[:4] if i != '']
                    recorded_signals_local_cache.append(msg)
                except ValueError:
                    print("ERROR: Could not convert string to int")
                    print(msg)

            lock_aquired = lock.acquire(False)

            if lock_aquired and recorded_signals_local_cache:
                #transfer recorded_signals_local_cache to recorded_signals
                recorded_signals.extend(recorded_signals_local_cache)
                recorded_signals_local_cache = []
                lock.release()
            elif lock_aquired:
                lock.release()

