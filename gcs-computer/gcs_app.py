import asyncio
import json
import random
import tkinter as tk
from datetime import datetime

import matplotlib.pyplot as plt
from app_models import TemperatureStatus
from gcs_server import ServerStatus
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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

        # Values shown
        self.server_status = ServerStatus.WAITING_FOR_CLIENT

        self.create_widgets()

    async def run(self):

        FPS = 24

        while True:
            self.root.update()
            await asyncio.sleep(1/FPS)

    def create_widgets(self):

        # Section that shows server status
        server_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        server_frame.grid(row=0, column=0, padx=10, pady=10)
        tk.Label(server_frame, text="Server").grid(row=0, column=0)
        self.server_status_label = tk.Label(server_frame, text=self.server_status.value)
        self.server_status_label.grid(row=1, column=0, pady=5)

        # Section that shows raw data received
        raw_data_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        raw_data_frame.grid(row=1, column=0, padx=10, pady=10)
        tk.Label(raw_data_frame, text="Raw data received").grid(row=0, column=0)
        self.raw_data_label = tk.Label(raw_data_frame, text="Waiting for data...", width=40, height=1)
        self.raw_data_label.grid(row=1, column=0, pady=5)
        self.received_time_label = tk.Label(raw_data_frame, text="Time: " + datetime.now().strftime("%H:%M:%S"))
        self.received_time_label.grid(row=2, column=0, pady=5)
        

        # Section shows plot of data received
        figure1 = plt.Figure(figsize=(16, 10), dpi=50)
        ax = figure1.add_subplot(111)
        self.spectogram_window = FigureCanvasTkAgg(figure1, self.root)
        self.spectogram_window.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, rowspan=5)
        ax.set_title("Spectogram")
        ax.plot([1, 2, 3, 4, 5, 6, 7])
        self.spectogram_window.draw()
        self.spectogram_ax = ax

        # Section with buttons and text
        button_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        button_frame.grid(row=2, column=0, padx=10, pady=10)
        tk.Label(button_frame, text="Commands").grid(row=0, column=0, columnspan=3)
        tk.Button(button_frame, text="Turn On override", command=self.send_override_on).grid(row=1, column=1, pady=5, padx=5)
        tk.Button(button_frame, text="Turn Off override", command=self.send_override_off).grid(row=1, column=2, pady=5, padx=5)
        tk.Button(button_frame, text="Toggle cooling fans").grid(row=2, column=1, pady=5, padx=5)
        self.power_limit = tk.IntVar()
        self.processing_power_slider = tk.Scale(button_frame, from_=0, to=100, variable=self.power_limit, orient=tk.HORIZONTAL).grid(row=2, column=2, pady=5, padx=5)
        tk.Button(button_frame, text="Limit processing power", command=self.send_processing_power_limit).grid(row=3, column=1, pady=5, padx=5)
        tk.Button(button_frame, text="Unlimit processing power", command=self.send_processing_power_unlimit).grid(row=3, column=2, pady=5, padx=5)

        # Section that shows real-time data
        data_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        data_frame.grid(row=3, column=0, padx=10, pady=10)
        tk.Label(data_frame, text="Real-time Data").grid(row=0, column=0)
        self.real_time_data_label = tk.Label(data_frame, text="Waiting for data...")
        self.real_time_data_label.grid(row=1, column=0, pady=5)

        # Section that shows temperature and fan speed
        sensor_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        sensor_frame.grid(row=4, column=0, padx=10, pady=10)
        tk.Label(sensor_frame, text="Temperature and Fan Speed").grid(row=0, column=0, columnspan=2)

        self.override_status_label = tk.Label(sensor_frame, text="Override Status: OFF")
        self.override_status_label.grid(row=1, column=0, pady=5)

        self.temperature_label = tk.Label(sensor_frame, text="Temperature: --")
        self.temperature_label.grid(row=1, column=1, pady=5)

        self.fan1_speed_label = tk.Label(sensor_frame, text="Fan 1 speed: --")
        self.fan1_speed_label.grid(row=2, column=0, pady=5)

        self.fan2_speed_label = tk.Label(sensor_frame, text="Fan 2 speed: --")
        self.fan2_speed_label.grid(row=2, column=1, pady=5)

        self.fan1_status_label = tk.Label(sensor_frame, text="Fan Status: OFF")
        self.fan1_status_label.grid(row=3, column=0, pady=5)

        self.fan2_status_label = tk.Label(sensor_frame, text="Fan Status: OFF")
        self.fan2_status_label.grid(row=3, column=1, pady=5)

    def send_processing_power_limit(self):
        self.send_command({
            "type": "PROCESSING_POWER",
            "action": "SET_LIMIT",
            "value": 1200
        })

    def send_processing_power_unlimit(self):
        self.send_command({
            "type": "PROCESSING_POWER",
            "action": "UNLIMIT",
            "value": 1
        })

    def send_override_on(self):
        self.send_command({
            "type": "TEMPERATURE",
            "action": "OVERRIDE",
            "value": True	
        })

    def send_override_off(self):
        self.send_command({
            "type": "TEMPERATURE",
            "action": "OVERRIDE",
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
        self.real_time_data_label.config(text="Real-time data: " + str(random.randint(1, 100)))

    def update_server_status(self, status):
        # Function to update server status label
        self.server_status = status
        self.server_status_label.config(text=self.server_status.value)

    def update_data(self, data):
        # Function to update raw data label
        self.raw_data_label.config(text=data)
        self.received_time_label.config(text="Time: " + datetime.now().strftime("%H:%M:%S"))

    def update_temperature_status_frame(self):
        # Function to update temperature label
        self.temperature_label.config(text="Temperature: " + str(self.temperature_status.current_temperature))
        self.fan1_speed_label.config(text="Fan 1 speed: " + str(self.temperature_status.fan_speed[0]))
        self.fan2_speed_label.config(text="Fan 2 speed: " + str(self.temperature_status.fan_speed[1]))
        self.fan1_status_label.config(text="Fan Status: " + ("ON" if self.temperature_status.fan_active[0] else "OFF"))
        self.fan2_status_label.config(text="Fan Status: " + ("ON" if self.temperature_status.fan_active[1] else "OFF"))
        self.override_status_label.config(text="Override Status: " + ("ON" if self.temperature_status.override_mode else "OFF"))
        
    async def update_spectogram_task(self):
        while True:
            self.draw_spectogram()
            await asyncio.sleep(1)

    async def update_task(self):
        while True:
            self.update_real_time_data()
            self.update_temperature_status_frame()
            await asyncio.sleep(1)

    def set_temperature_status(self, data):
        self.temperature_status.current_temperature = data["current_temperature"]
        self.temperature_status.fan_speed = data["fan_speed"]
        self.temperature_status.activate_fan = data["fan_active"]
        self.temperature_status.override_mode = data["override_mode"]