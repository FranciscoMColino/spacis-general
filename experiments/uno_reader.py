import time

import serial

# Replace 'COM3' with the actual COM port of your Arduino
# 9600 is the default baud rate for most Arduino sketches
ser = serial.Serial('COM9', 2000000)

message_count = 0
start_time = time.time()

try:
    while True:
        # Read a line from the serial port
        line = ser.readline().decode('utf-8').strip()

        # Update the message count
        message_count += 1

        # Print the received data
        # print(line)

        # Calculate and print the average message frequency
        elapsed_time = time.time() - start_time
        if elapsed_time > 5:  # Calculate average over a 5-second window
            average_frequency = message_count / elapsed_time
            print("line: ", line)
            print(
                f"Average Message Frequency: {average_frequency:.2f} messages per second")
            # Reset counters
            message_count = 0
            start_time = time.time()
except KeyboardInterrupt:
    # Handle Ctrl+C gracefully, closing the serial connection
    ser.close()
