import asyncio
import random
import tkinter as tk


async def test_task():
    while True:
        print("Performing test task...")
        await asyncio.sleep(1)

class App:
    def __init__(self, root, loop):
        self.loop = loop
        self.root = root
        self.root.title("Fan Control Panel")
        self.create_widgets()

    async def run(self):

        FPS = 24

        while True:
            self.root.update()
            await asyncio.sleep(1/FPS)

    def create_widgets(self):
        # Section with buttons and text
        button_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        button_frame.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(button_frame, text="Commands").pack()
        tk.Button(button_frame, text="Start").pack(pady=5)
        tk.Button(button_frame, text="Stop").pack(pady=5)
        tk.Button(button_frame, text="Pause").pack(pady=5)
        
        # Section that shows real-time data
        data_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        data_frame.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(data_frame, text="Real-time Data").pack()
        self.real_time_data_label = tk.Label(data_frame, text="Waiting for data...")
        self.real_time_data_label.pack(pady=5)

        # Section that shows temperature and fan speed
        sensor_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        sensor_frame.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(sensor_frame, text="Temperature and Fan Speed").pack()
        self.temperature_label = tk.Label(sensor_frame, text="Temperature: --")
        self.temperature_label.pack(pady=5)
        self.fan_speed_label = tk.Label(sensor_frame, text="Fan Speed: --")
        self.fan_speed_label.pack(pady=5)
        self.fan_status_label = tk.Label(sensor_frame, text="Fan Status: OFF")
        self.fan_status_label.pack(pady=5)

    def update_real_time_data(self):
        # Function to update real-time data label with random value
        self.real_time_data_label.config(text="Real-time data: " + str(random.randint(1, 100)))
        print("Updating real-time data...")

    async def update_task(self):
        while True:
            self.update_real_time_data()
            await asyncio.sleep(1)

async def main():
    root = tk.Tk()
    root.geometry("400x400")
    app = App(root ,asyncio.get_event_loop())

    asyncio.create_task(app.run())
    asyncio.create_task(app.update_task())
    
    while True:
        try:
            print("Performing main task...")
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break

asyncio.run(main())
