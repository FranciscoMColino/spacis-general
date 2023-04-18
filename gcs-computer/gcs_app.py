import asyncio
import random
import tkinter as tk

from gcs_server import ServerStatus


async def test_task():
    while True:
        print("Performing test task...")
        await asyncio.sleep(1)

class GCSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fan Control Panel")

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
        self.real_time_data_label = tk.Label(server_frame, text=self.server_status.value)
        self.real_time_data_label.grid(row=1, column=0, pady=5)

        # Section with buttons and text
        button_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        button_frame.grid(row=0, column=1, padx=10, pady=10)
        tk.Label(button_frame, text="Commands").grid(row=0, column=0)
        tk.Button(button_frame, text="Start").grid(row=1, column=0, pady=5)
        tk.Button(button_frame, text="Stop").grid(row=2, column=0, pady=5)
        tk.Button(button_frame, text="Pause").grid(row=3, column=0, pady=5)

        # Section that shows real-time data
        data_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        data_frame.grid(row=1, column=0, padx=10, pady=10)
        tk.Label(data_frame, text="Real-time Data").grid(row=0, column=0)
        self.real_time_data_label = tk.Label(data_frame, text="Waiting for data...")
        self.real_time_data_label.grid(row=1, column=0, pady=5)

        # Section that shows temperature and fan speed
        sensor_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        sensor_frame.grid(row=1, column=1, padx=10, pady=10)
        tk.Label(sensor_frame, text="Temperature and Fan Speed").grid(row=0, column=0)
        self.temperature_label = tk.Label(sensor_frame, text="Temperature: --")
        self.temperature_label.grid(row=1, column=0, pady=5)
        self.fan_speed_label = tk.Label(sensor_frame, text="Fan Speed: --")
        self.fan_speed_label.grid(row=2, column=0, pady=5)
        self.fan_status_label = tk.Label(sensor_frame, text="Fan Status: OFF")
        self.fan_status_label.grid(row=3, column=0, pady=5)


    def update_real_time_data(self):
        # Function to update real-time data label with random value
        self.real_time_data_label.config(text="Real-time data: " + str(random.randint(1, 100)))
        print("Updating real-time data...")

    def update_server_status(self, status):
        # Function to update server status label
        self.server_status = status
        self.server_status_label.config(text=self.server_status.value)

    async def update_task(self):
        while True:
            self.update_real_time_data()
            await asyncio.sleep(1)