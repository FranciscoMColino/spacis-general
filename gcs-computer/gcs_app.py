import asyncio
import json
import random
import tkinter as tk
from datetime import datetime

import matplotlib.pyplot as plt
from app_models import CommandActionsState, GpsStatus, TemperatureStatus
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

UPDATE_UI_INTERVAL = 1/12

async def test_task():
    while True:
        print("Performing test task...")
        await asyncio.sleep(1)

class GCSApp:
    def __init__(self, root, data_manager, server):
        self.root = root
        self.root.title("Fan Control Panel")
        self.server = server
        self.data_manager = data_manager
        self.temperature_status = TemperatureStatus()
        self.command_actions_state = CommandActionsState()
        self.gps_status = GpsStatus()
        self.display_data = []

        # Values shown
        self.server_client_status = self.server.client

        self.create_widgets()

    async def run(self):

        FPS = 24

        while True:
            self.root.update()
            await asyncio.sleep(1/FPS)

    def create_widgets(self):

        # Section that shows server status
        server_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        server_frame.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(server_frame, text="Server").grid(row=0, column=0)
        self.server_status_label = tk.Label(server_frame, text="Waiting for client...")
        self.server_status_label.grid(row=1, column=0, pady=5)
        self.client_last_update_label = tk.Label(server_frame, text="Last update: ---")
        self.client_last_update_label.grid(row=2, column=0, pady=5)

        # Section shows plot of data received
        figure1 = plt.Figure(figsize=(16, 10), dpi=50)
        ax = figure1.add_subplot(111)
        self.spectogram_window = FigureCanvasTkAgg(figure1, self.root)
        self.spectogram_window.get_tk_widget().grid(row=0, column=2, padx=10, pady=10, rowspan=5)
        ax.set_title("Spectogram")
        ax.plot([1, 2, 3, 4, 5, 6, 7])
        self.spectogram_window.draw()
        self.spectogram_ax = ax

        # Section with buttons and text
        button_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        button_frame.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(button_frame, text="Commands").grid(row=0, column=0, columnspan=3)


        self.override_status_label = tk.Label(button_frame, text="Override Status: OFF")
        self.override_status_label.grid(row=1, column=0, pady=5)
        self.override_toggle = tk.Button(button_frame, text="Turn ON", command=self.toggle_override)
        self.override_toggle.grid(row=1, column=1, pady=5, padx=5)

        tk.Button(button_frame, text="Config CPU clock (MHz)", command=self.set_cpu_clock).grid(row=4, column=0, pady=5, padx=5)
        self.command_actions_state.cpu_clock = tk.IntVar()
        self.cpu_clock_slider = tk.Scale(button_frame, from_=600, to=2200, variable=self.command_actions_state.cpu_clock, orient=tk.HORIZONTAL, resolution=100)
        self.cpu_clock_slider.grid(row=4, column=1, pady=5, padx=5)

        tk.Button(button_frame, text="Reboot RPI" , command=self.reboot_rpi).grid(row=5, column=0, pady=5, padx=5)
        
        # Section that shows temperature and fan speed
        sensor_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        sensor_frame.grid(row=2, column=0, padx=10, pady=10)
        tk.Label(sensor_frame, text="Temperature control").grid(row=0, column=0, columnspan=2)

        box_temp_frame = tk.Frame(sensor_frame, bd=1, relief=tk.SOLID)
        box_temp_frame.grid(row=1, column=0, pady=5, padx=5)
        tk.Label(box_temp_frame, text="Box", font='Segoe 9 bold').grid(row=0, column=0)

        self.box_temperature_label = tk.Label(box_temp_frame, text="Box temp.: --")
        self.box_temperature_label.grid(row=1, column=0, pady=5)

        self.box_fan_label = tk.Label(box_temp_frame, text="Box fans: OFF")
        self.box_fan_label.grid(row=2, column=0, pady=5)

        self.box_fan_toggle = tk.Button(box_temp_frame, text="Turn ON", command=self.toggle_box_fans)
        self.box_fan_toggle.grid(row=3, column=0, pady=5, padx=5)

        rpi_temp_frame = tk.Frame(sensor_frame, bd=1, relief=tk.SOLID)
        rpi_temp_frame.grid(row=1, column=1, pady=5, padx=5)
        tk.Label(rpi_temp_frame, text="RPi", font='Segoe 9 bold').grid(row=0, column=0)

        self.cpu_temperature_label = tk.Label(rpi_temp_frame, text="CPU temp.: --")
        self.cpu_temperature_label.grid(row=1, column=0, pady=5)

        self.rpi_fan_label = tk.Label(rpi_temp_frame, text="RPi fans: OFF")
        self.rpi_fan_label.grid(row=2, column=0, pady=5)

        self.rpi_fan_toggle = tk.Button(rpi_temp_frame, text="Turn ON", command=self.toggle_rpi_fans)
        self.rpi_fan_toggle.grid(row=3, column=0, pady=5, padx=5)

        # Section for gps data
        gps_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        gps_frame.grid(row=2, column=1, padx=10, pady=10)
        tk.Label(gps_frame, text="GPS Data").grid(row=0, column=0, columnspan=2)

        self.gps_latitude_label = tk.Label(gps_frame, text="Latitude: --")
        self.gps_latitude_label.grid(row=1, column=0, pady=5)

        self.gps_longitude_label = tk.Label(gps_frame, text="Longitude: --")
        self.gps_longitude_label.grid(row=2, column=0, pady=5)


        # Section that shows raw data received
        raw_data_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        raw_data_frame.grid(row=3, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(raw_data_frame, text="Raw data received").grid(row=0, column=0)
        self.rcv_data_txt = tk.Text(raw_data_frame, height=10, width=50)
        self.rcv_data_txt.grid(row=1, column=0, pady=5, padx=5)
        #self.rcv_data_txt.insert(tk.END, "Waiting for data...")
        self.rcv_data_txt.config(state=tk.DISABLED)
        self.received_time_label = tk.Label(raw_data_frame, text="Time: " + datetime.now().strftime("%H:%M:%S"))
        self.received_time_label.grid(row=2, column=0, pady=5)

        # Section that shows real-time data
        #data_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        #data_frame.grid(row=4, column=0, padx=10, pady=10)
        #tk.Label(data_frame, text="Real-time Data").grid(row=0, column=0)
        #self.real_time_data_label = tk.Label(data_frame, text="Waiting for data...")
        #self.real_time_data_label.grid(row=1, column=0, pady=5)

    # Button/action functions

    def toggle_override(self):
        print("LOG: Toggle override button pressed")
        if self.temperature_status.override_mode == True:
            self.send_override_off()
        else:
            self.send_override_on()

    def toggle_rpi_fans(self):
        print("LOG: Toggle RPi fans button pressed")
        if self.temperature_status.rpi_fan == True:
            self.send_rpi_fan_off()
        else:
            self.send_rpi_fan_on()

    def toggle_box_fans(self):
        print("LOG: Toggle box fans button pressed")
        if self.temperature_status.box_fan == True:
            self.send_box_fan_off()
        else:
            self.send_box_fan_on()

    def set_cpu_clock(self):
        print("LOG: Set CPU clock button pressed")
        self.send_cpu_clock(self.command_actions_state.cpu_clock.get())

    def reboot_rpi(self):
        print("LOG: Reboot RPI button pressed")
        self.send_reboot_rpi()
        
    # Functions to send commands to the server

    def send_processing_power_limit(self):
        print("LOG: Limit processing power button pressed")
        self.send_command({
            "type": "PROCESSING_POWER",
            "action": "SET_LIMIT",
            "value": 1200
        })

    def send_processing_power_unlimit(self):
        print("LOG: Unlimit processing power button pressed")
        self.send_command({
            "type": "PROCESSING_POWER",
            "action": "UNLIMIT",
            "value": 1
        })

    def send_override_on(self):
        print("LOG: Override on button pressed")
        self.send_command({
            "type": "TEMPERATURE",
            "action": "OVERRIDE",
            "value": True	
        })

    def send_override_off(self):
        print("LOG: Override off button pressed")
        self.send_command({
            "type": "TEMPERATURE",
            "action": "OVERRIDE",
            "value": False	
        })

    def send_cpu_clock(self, clock):
        print("LOG: CPU clock button pressed")
        self.send_command({
            "type": "OS",
            "action": "SET_CPU_SPEED",
            "value": clock
        })

    def send_reboot_rpi(self):
        print("LOG: Reboot RPI button pressed")
        self.send_command({
            "type": "OS",
            "action": "REBOOT",
            "value": True
        })

    def send_rpi_fan_on(self):
        print("LOG: RPi fan on button pressed")
        self.send_command({
            "type": "TEMPERATURE",
            "action": "RPI_FAN_ACTIVE",
            "value": True
        })
    
    def send_rpi_fan_off(self):
        print("LOG: RPi fan off button pressed")
        self.send_command({
            "type": "TEMPERATURE",
            "action": "RPI_FAN_ACTIVE",
            "value": False
        })

    def send_box_fan_on(self):
        print("LOG: Box fan on button pressed")
        self.send_command({
            "type": "TEMPERATURE",
            "action": "BOX_FAN_ACTIVE",
            "value": True
        })

    def send_box_fan_off(self):
        print("LOG: Box fan off button pressed")
        self.send_command({
            "type": "TEMPERATURE",
            "action": "BOX_FAN_ACTIVE",
            "value": False
        })    

    def send_command(self, command):
        
        obj = {
            "type": "command",
            "data": command
        }
        self.server.send_message(json.dumps(obj))

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

    def update_real_time_data(self):
        # Function to update real-time data label with random value
        #self.real_time_data_label.config(text="Real-time data: " + str(random.randint(1, 100)))
        pass

    def update_server_status(self):
        # Function to update server status label
        if (self.server.client.connected):
            self.server_status_label.config(text="Client Connected")
            # change color to green
            self.server_status_label.config(bg="green")
        else:
            self.server_status_label.config(text="Client Disconnected")
            # change color to red
            self.server_status_label.config(bg="red")
        
        self.client_last_update_label.config(text="Last update: " + self.server.client.last_update)

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

    def update_temperature_status_frame(self):
        # Function to update temperature label
        self.box_temperature_label.config(text="Box temp.: " + str(self.temperature_status.box_temperature))
        self.cpu_temperature_label.config(text="CPU temp.: " + str(self.temperature_status.cpu_temperature))

        self.box_fan_label.config(text="Box Fan: " + ("ON" if self.temperature_status.box_fan else "OFF"))
        self.rpi_fan_label.config(text="RPi Fan: " + ("ON" if self.temperature_status.rpi_fan else "OFF"))


        if self.temperature_status.box_fan == True:
            self.box_fan_toggle.config(text="Turn OFF")
        else:
            self.box_fan_toggle.config(text="Turn ON")

        if self.temperature_status.rpi_fan == True:
            self.rpi_fan_toggle.config(text="Turn OFF")
        else:
            self.rpi_fan_toggle.config(text="Turn ON")
        
        if self.temperature_status.override_mode == True:
            self.override_toggle.config(text="Turn OFF")
        else:
            self.override_toggle.config(text="Turn ON")
        
    def update_gps_status_frame(self):
        # Function to update GPS label
        self.gps_latitude_label.config(text="Latitude: " + str(self.gps_status.latitude))
        self.gps_longitude_label.config(text="Longitude: " + str(self.gps_status.longitude))

    def update_command_buttons(self):
        if self.temperature_status.override_mode == True:
            self.override_toggle.config(text="Turn OFF")
        else:
            self.override_toggle.config(text="Turn ON")

        self.override_status_label.config(text="Override Status: " + ("ON" if self.temperature_status.override_mode else "OFF"))
        
    async def update_spectogram_task(self):
        while True:
            self.draw_spectogram()
            await asyncio.sleep(1)

    

    async def update_task(self):
        while True:
            self.update_real_time_data()
            self.update_temperature_status_frame()
            self.update_command_buttons()
            self.update_server_status()
            self.update_gps_status_frame()
            await asyncio.sleep(UPDATE_UI_INTERVAL)

    def set_temperature_status(self, data):
        self.temperature_status.cpu_temperature = round(data["cpu_temperature"], 2)
        self.temperature_status.box_temperature = round(data["box_temperature"], 2)

        self.temperature_status.box_fan = data["box_fan"]
        self.temperature_status.rpi_fan = data["rpi_fan"]
        self.temperature_status.override_mode = data["override_mode"]
    
    def set_gps_status(self, data):
        self.gps_status.latitude = data["lat"]
        self.gps_status.longitude = data["lon"]