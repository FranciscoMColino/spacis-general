import asyncio
import json
import tkinter as tk
from datetime import datetime
from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

SUB_DISTANCE = 2.55
UPDATE_UI_INTERVAL = 1/12

class GpsStatus:
    def __init__(self):
        self.latitude = 0
        self.longitude = 0

class SSApp:
    def __init__(self, root, serial_com, data_manager):
        self.root = root
        self.root.title("Sound Station")
        self.serial_com = serial_com
        self.data_manager = data_manager
        self.display_data = []
        self.gps_status = GpsStatus()
        self.create_widgets()

    def calculate_angle_2_subs(self, frame):

        # TODO hardcoded for now
        sub_distance = SUB_DISTANCE
        delay_sub_0 = self.delay_control.entry_boxes[4].get()
        delay_sub_1 = self.delay_control.entry_boxes[5].get()

        if not delay_sub_0 or not delay_sub_1:
            print("No delay cycles entered") # TODO log in UI
            return 0

        delay_cycles = int(delay_sub_1) - int(delay_sub_0)
        print("Delay cycles: {}".format(delay_cycles))

        # speed of sound in air
        c = 343.0
        delay_between_tx = 1/1600 # in seconds
        distance_traveled = c * delay_between_tx * delay_cycles

        print("Distance traveled: {} meters".format(distance_traveled))

        transmission_angle = np.rad2deg(np.pi/2-np.arctan(distance_traveled/sub_distance))

        #round transmission angle to 4 decimal places
        transmission_angle = round(transmission_angle, 4)

        frame.result_label.config(text="Tx angle: " + str(transmission_angle))

    def send_delays(self):

        value_array = self.convert_entries_to_values(self.delay_control.entry_boxes)

        # check if size 6
        if len(value_array) != 6:
            print("Incorrect size of array")
            return

        message = 'A ' + ' '.join(str(num) for num in value_array)  # 'A' represents the type of message

        print("Message sent: ", message)

        self.serial_com.send_message(message.encode())

    def update_elements(self):
        joined_messages = "\n".join(self.serial_com.get_received_messages()[-8::])
        self.text_entry.config(state=tk.NORMAL)
        self.text_entry.delete("1.0", tk.END)
        self.text_entry.insert(tk.END, joined_messages)
        self.text_entry.config(state=tk.DISABLED)

    async def run(self):

        FPS = 24

        while True:
            self.update_elements()
            self.root.update()
            await asyncio.sleep(1/FPS)

    def convert_entries_to_values(self, entries):
        values = []
        for entry in entries:
            
            value = int(entry.get())

            try:
                value = int(value)
            except ValueError:
                return False
            values.append(value)
        return values
    
    def create_gps_frames(self):
         ##### Section for gps data

        gps_control_frame = tk.Frame(self.root, bd=1, relief=tk.FLAT)
        gps_control_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        gps_frame = tk.Frame(gps_control_frame, bd=1, relief=tk.SOLID)
        gps_frame.grid(row=0, column=0, padx=10, pady=10)
        tk.Label(gps_frame, text="GPS Data").grid(row=0, column=0, columnspan=2)

        self.gps_latitude_label = tk.Label(gps_frame, text="Latitude: --")
        self.gps_latitude_label.grid(row=1, column=0, pady=5)

        self.gps_longitude_label = tk.Label(gps_frame, text="Longitude: --")
        self.gps_longitude_label.grid(row=2, column=0, pady=5)

        ###### Section for manual control
        delay_frame = tk.Frame(gps_control_frame, bd=1, relief=tk.SOLID)
        delay_frame.grid(row=1, column=0, padx=10, pady=10)

        title = tk.Label(delay_frame, text="Calculate angle between two subs")
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        class DelayControl:
            pass

        self.delay_control = DelayControl()


        self.delay_control.entry_boxes = []

        for i in range(6):
            label = tk.Label(delay_frame, text="Value " + str(i+1))
            label.grid(row=i+1, column=0, padx=10, pady=5)
            entry = tk.Entry(delay_frame)
            entry.grid(row=i+1, column=1, padx=10, pady=5)

            if entry.get() == "":
                entry.insert(0, "0")

            self.delay_control.entry_boxes.append(entry)

        calculate_button = tk.Button(delay_frame, text="Calculate angle", command= partial(self.calculate_angle_2_subs, delay_frame))
        calculate_button.grid(row=7, column=0, padx=10, pady=10)

        delay_frame.result_label = tk.Label(delay_frame, text="Tx angle: ")
        delay_frame.result_label.grid(row=7, column=1, padx=10, pady=10)

        send_button = tk.Button(delay_frame, text="Send delays", command= self.send_delays)
        send_button.grid(row=8, column=0, padx=10, pady=10 , columnspan=2)

    def create_log_frames(self):

        logs_frame = tk.Frame(self.root, bd=1, relief=tk.FLAT)
        logs_frame.grid(row=0, column=1, padx=10, pady=10)

        ##### frame that shows the last 8 messages from the serial_com
        serial_com_frame = tk.Frame(logs_frame, bd=1, relief=tk.FLAT)
        serial_com_frame.grid(row=0, column=0, padx=5, pady=5)

        serial_com_frame_title = tk.Label(serial_com_frame, text="Serial Com")
        serial_com_frame_title.grid(row=0, column=0, padx=5, pady=5)

        joined_messages = "\n".join(self.serial_com.get_received_messages())
        self.text_entry = tk.Text(serial_com_frame, height=10, width=30)
        self.text_entry.grid(row=1, column=0, padx=5, pady=5)
        self.text_entry.insert(tk.END, joined_messages)
        self.text_entry.config(state=tk.DISABLED)
        #text_entry.grid(row=0, column=0, padx=10, pady=10)

        # ##### SYSTEM LOGS ##### #

        system_logs_frame = tk.Frame(logs_frame, bd=1, relief=tk.FLAT)
        system_logs_frame.grid(row=1, column=0, padx=5, pady=5)

        system_logs_frame_title = tk.Label(system_logs_frame, text="System Logs")
        system_logs_frame_title.grid(row=0, column=0, padx=5, pady=5)

        system_logs_text = tk.Text(system_logs_frame, height=10, width=30)
        system_logs_text.grid(row=1, column=0, padx=5, pady=5)
        system_logs_text.insert(tk.END, "System logs")
        system_logs_text.config(state=tk.DISABLED)

        # Section that shows raw data received
        raw_data_frame = tk.Frame(system_logs_frame, bd=1, relief=tk.FLAT)
        raw_data_frame.grid(row=2, column=0, padx=5, pady=5)

        system_logs_frame_title = tk.Label(system_logs_frame, text="Sensor data received")
        system_logs_frame_title.grid(row=0, column=0, padx=5, pady=5)

        tk.Label(raw_data_frame, text="Raw data received").grid(row=0, column=0)
        self.rcv_data_txt = tk.Text(raw_data_frame, height=10, width=30)
        self.rcv_data_txt.grid(row=1, column=0, pady=5, padx=5)
        #self.rcv_data_txt.insert(tk.END, "Waiting for data...")
        self.rcv_data_txt.config(state=tk.DISABLED)
        self.received_time_label = tk.Label(raw_data_frame, text="Time: " + datetime.now().strftime("%H:%M:%S"))
        self.received_time_label.grid(row=2, column=0, pady=5)

    def create_dataviz_frame(self):

        dataviz_frame = tk.Frame(self.root, bd=1, relief=tk.FLAT)
        dataviz_frame.grid(row=0, column=2, padx=10, pady=10)

        # Section shows plot of data received
        figure1 = plt.Figure(figsize=(16, 10), dpi=50)
        ax = figure1.add_subplot(111)
        self.spectogram_window = FigureCanvasTkAgg(figure1, dataviz_frame)
        self.spectogram_window.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, rowspan=5)
        ax.set_title("Spectogram")
        ax.plot([1, 2, 3, 4, 5, 6, 7])
        self.spectogram_window.draw()
        self.spectogram_ax = ax

        

    def create_widgets(self):
       
        self.create_gps_frames()
        self.create_log_frames()
        self.create_dataviz_frame()

    def draw_spectogram(self):
        SAMPLE_SIZE = pow(2, 12) * 4 * 1.1

        if not self.data_manager.local_data:
            return

        data = list(zip(*self.data_manager.local_data))[0]

        display_data = []
        if len(data) > SAMPLE_SIZE:
            display_data = data[len(data)-int(SAMPLE_SIZE):]
        else:
            display_data = data

        self.spectogram_ax.clear()
        self.spectogram_ax.specgram(display_data, Fs=1600, vmin=-5, vmax=30)
        self.spectogram_ax.set_ylim([0, 100])
        self.spectogram_window.draw()

    def update_data(self, data):
        # Function to update raw data label

        self.display_data.append(data)

        if len(self.display_data) > 10:
            self.display_data.pop(0)
        
        self.rcv_data_txt.config(state=tk.NORMAL)
        self.rcv_data_txt.delete("1.0", tk.END)

        for d in self.display_data:
            self.rcv_data_txt.insert(tk.END,"Number of samples {}\n".format(len(d)))

        self.rcv_data_txt.config(state=tk.DISABLED)

        self.received_time_label.config(text="Time: " + datetime.now().strftime("%H:%M:%S"))

    async def update_spectogram_task(self):
        while True:
            self.draw_spectogram()
            await asyncio.sleep(UPDATE_UI_INTERVAL)

    def update_gps_status(self):
        # Function to update GPS label
        self.gps_latitude_label.config(text="Latitude: " + str(self.gps_status.latitude))
        self.gps_longitude_label.config(text="Longitude: " + str(self.gps_status.longitude))

    async def update_task(self):
        while True:
            self.update_gps_status()
            print("LOG: update task not implemented yet")
            await asyncio.sleep(UPDATE_UI_INTERVAL)

    def set_gps_status(self, data):
        self.gps_status.latitude = data["lat"]
        self.gps_status.longitude = data["lon"]

    

        


        
        