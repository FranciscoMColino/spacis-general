import asyncio
import datetime

import serial.tools.list_ports

AUTO_DETECT = True
MANUAL_SERIAL_PORT = "COM8"
MAX_NO_RCV = 100

serial_reading = True

class TransmitterSerial():
    def __init__(self, data_recorder):
        self.baundrate = 115200
        self.received_messages = []
        self.data_recorder = data_recorder
    
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
        
        while True:
            
            while ser.in_waiting > 0:
                msg = ser.readline().decode('utf-8').rstrip()
                self.received_messages.append(msg)
                if len(self.received_messages) > MAX_NO_RCV:
                    self.received_messages = self.received_messages[len(self.received_messages)-MAX_NO_RCV:]
                # split message by :
                msg_split = msg.split(':')

                if len(msg_split) != 2:
                    continue

                msg_type, msg_body = msg_split[0], msg_split[1]

                if msg_type == "SEQ_TX":
                    data = msg_body.split(',')
                    #strip spaces
                    data = [x.strip() for x in data]
                    data.append(datetime.datetime.now().strftime("%H-%M-%S")+ f".{datetime.datetime.now().microsecond // 1000:03d}")
                    self.data_recorder.record_transmitted_data(data)

            await asyncio.sleep(2)
