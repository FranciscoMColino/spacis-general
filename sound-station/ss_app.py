import asyncio
import json
import tkinter as tk
from functools import partial

import numpy as np


class SSApp:
    def __init__(self, root, serial_com):
        self.root = root
        self.root.title("Sound Station")
        self.serial_com = serial_com
        #self.server = server TODO
        #self.data_manager = data_manager TODO

        # Values shown
        #self.server_status = ServerStatus.WAITING_FOR_CLIENT TODO

        self.create_widgets()

    def calculate_angle_2_subs(self, frame):

        # TODO hardcoded for now
        sub_distance = 1
        delay_sub_0 = self.delay_control.entry_boxes[0].get()
        delay_sub_1 = self.delay_control.entry_boxes[1].get()

        if not delay_sub_0 or not delay_sub_1:
            print("No delay cycles entered") # TODO log in UI
            return 0
        else:
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

    def send_delays(self, value_array):
        # check if size 6
        if len(value_array) != 6:
            print("Incorrect size of array")
            return
        
        data = {
            "command": "DELAYS",
            "values": value_array
        }

        json_message = json.dumps(data)

        self.serial_com.send_message(json_message.encode())

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


    def create_widgets(self):
        # Section with buttons and text

        # ##### FRAME FOR DELAY CONTROL ##### #
        
        delay_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        delay_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

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

        # Create calculate button
        calculate_button = tk.Button(delay_frame, text="Calculate angle", command= partial(self.calculate_angle_2_subs, delay_frame))
        calculate_button.grid(row=7, column=0, padx=10, pady=10)

        # Create result label
        delay_frame.result_label = tk.Label(delay_frame, text="Tx angle: ")
        delay_frame.result_label.grid(row=7, column=1, padx=10, pady=10)

        # Send delays button
        send_button = tk.Button(delay_frame, text="Send delays", command= partial(self.send_delays, self.convert_entries_to_values(self.delay_control.entry_boxes)))
        send_button.grid(row=8, column=0, padx=10, pady=10 , columnspan=2)

        # ##### SERIAL COM MONITOR ##### #

        # frame that shows the last 8 messages from the serial_com
        serial_com_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        serial_com_frame.grid(row=0, column=1, padx=10, pady=10)

        serial_com_frame_title = tk.Label(serial_com_frame, text="Serial Com")
        serial_com_frame_title.grid(row=0, column=0, padx=10, pady=10)

        joined_messages = "\n".join(self.serial_com.get_received_messages())
        self.text_entry = tk.Text(serial_com_frame, height=10, width=50)
        self.text_entry.grid(row=1, column=0, padx=10, pady=10)
        self.text_entry.insert(tk.END, joined_messages)
        self.text_entry.config(state=tk.DISABLED)
        #text_entry.grid(row=0, column=0, padx=10, pady=10)

        # ##### SYSTEM LOGS ##### #

        system_logs_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        system_logs_frame.grid(row=1, column=1, padx=10, pady=10)

        system_logs_frame_title = tk.Label(system_logs_frame, text="System Logs")
        system_logs_frame_title.grid(row=0, column=0, padx=10, pady=10)

        system_logs_text = tk.Text(system_logs_frame, height=10, width=50)
        system_logs_text.grid(row=1, column=0, padx=10, pady=10)
        system_logs_text.insert(tk.END, "System logs")
        system_logs_text.config(state=tk.DISABLED)


        
        