import asyncio

import serial.tools.list_ports

AUTO_DETECT = True
MANUAL_SERIAL_PORT = "COM8"

serial_reading = True

def kill_signal_generator():
    global serial_reading
    serial_reading = False

class TransmitterSerial():
    def __init__(self):
        self.baundrate = 115200
        self.received_messages = []
        self.data = []
    
    # TODO keep trying to connect, and deal with disconnects

    def connect(self):
        # Filter the list to find the port with "Arduino" in its description

        arduino_device = None

        if AUTO_DETECT:
            arduino_ports = [
                p.device
                for p in serial.tools.list_ports.comports()
                if 'Arduino' in p.description
            ]
            if (not arduino_ports):
                print("ERROR: No Arduino found")
                self.ser = None
                return False
            arduino_device = arduino_ports[0]

        else:
            arduino_device = MANUAL_SERIAL_PORT
        

        self.ser  = serial.Serial(arduino_device, self.baundrate)
        
        if self.ser:
            print("Connected successfully to the arduino", arduino_device)
            return True
        else:
            print("Failed to connect to the arduino")
            return False

    def get_received_messages(self):
        return self.received_messages

    def send_message(self, message):

        ser = self.ser

        if (not ser):
            print("ERROR: No serial port found")
            return

        ser.write(message)
        ser.write(b'\n')

    async def read_messages(self):

        ser = self.ser

        if (not ser):
            print("ERROR: No serial port found")
            return

        recorded_signals_local_cache = []
        global serial_reading

        while serial_reading:
            
            while ser.in_waiting > 0:
                msg = ser.readline().decode('utf-8').rstrip()
                recorded_signals_local_cache.append(msg)
                #print("Serial message: {}".format(msg))

            if recorded_signals_local_cache:
                #transfer recorded_signals_local_cache to recorded_signals
                self.received_messages.extend(recorded_signals_local_cache)
                recorded_signals_local_cache = []

            await asyncio.sleep(2)
