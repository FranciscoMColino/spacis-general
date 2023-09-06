import asyncio
import datetime

import serial.tools.list_ports

MAX_NO_RCV = 100

DELAY_SEND_WAIT_TIME = 2 # seconds

serial_reading = True

class TransmitterSerial():
    def __init__(self, data_recorder, delay_module, settings):
        self.baundrate = 115200
        self.received_messages = []
        self.data_recorder = data_recorder
        self.delay_module = delay_module
        self.manual_port_config = settings["manual_port_config"]
        self.manual_serial_port = settings["manual_serial_port"]
    
    # TODO keep trying to connect, and deal with disconnects

    def connect(self):
        # Filter the list to find the port with "Arduino" in its description
        try:
            arduino_device = None

            if not self.manual_port_config:
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
                arduino_device = self.manual_serial_port
            

            self.ser  = serial.Serial(arduino_device, self.baundrate)
            
            if self.ser:
                print("Connected successfully to the arduino", arduino_device)
                return True
            else:
                print("Failed to connect to the arduino with device", arduino_device)
                return False
        except Exception as e:
            print("Failed to connect to the arduino, ", e)
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

    def send_delays(self, values):

        #value_array = self.convert_entries_to_values(self.delay_module.delay_entries)
        
        # check if size 6
        if len(values) != 6:
            print("Incorrect size of array")
            return

        message = 'A ' + ' '.join(str(num) for num in values)  # 'A' represents the type of message

        print("Message sent: ", message)

        self.send_message(message.encode())

    async def periodic_send_delays(self): 

        last_sent = [-1, -1, -1, -1, -1, -1]
    
        while True:

            if self.delay_module.manual_send_var.get():
                last_sent = [-1, -1, -1, -1, -1, -1]
                await asyncio.sleep(DELAY_SEND_WAIT_TIME)
                continue

            delays = [self.delay_module.subwoofer_array["sub{}".format(i)]["delay"] for i in range(6)]

            if delays == last_sent:
                await asyncio.sleep(DELAY_SEND_WAIT_TIME)
                continue

            self.send_delays(delays)
            last_sent = delays
            
            await asyncio.sleep(DELAY_SEND_WAIT_TIME)

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
