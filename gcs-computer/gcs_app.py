import asyncio
import json
import random
import time
import tkinter as tk
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from app_models import (DataVizControl, GpsStatus, SystemControlData,
                        TemperatureStatus)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

UPDATE_UI_INTERVAL = 1/12
FPS = 24

async def test_task():
    while True:
        print("Performing test task...")
        await asyncio.sleep(1)

class GCSApp:
    def __init__(self, root, data_manager, server, performance_recordings):
        self.root = root
        self.root.title("Fan Control Panel")
        self.server = server
        self.data_manager = data_manager
        self.performance_recordings = performance_recordings
        self.temperature_status = TemperatureStatus()
        self.system_control_data = SystemControlData()
        self.data_viz_control = DataVizControl()
        self.gps_status = GpsStatus()
        self.received_sample_clusters = []
        self.received_samples = []

        # Values shown
        self.server_client_status = self.server.client

        self.create_widgets()

    async def run(self):

        while True:
            self.root.update()
            await asyncio.sleep(1/FPS)

    def create_server_status_widget(self):
        # Section that shows server status
        server_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        server_frame.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(server_frame, text="Server").grid(row=0, column=0)
        self.server_status_label = tk.Label(server_frame, text="Waiting for client...")
        self.server_status_label.grid(row=1, column=0, pady=5)
        self.client_last_update_label = tk.Label(server_frame, text="Last update: ---")
        self.client_last_update_label.grid(row=2, column=0, pady=5)
    
    def create_data_spec_widget(self):
        # Section shows plot of data received

        data_viz_frame = tk.Frame(self.root, bd=1, relief=tk.FLAT)
        data_viz_frame.grid(row=1, column=2, padx=10, pady=10, rowspan=4)

        figure1 = plt.Figure(figsize=(16, 10), dpi=50)
        ax = figure1.add_subplot(111)
        self.spectogram_window = FigureCanvasTkAgg(figure1, data_viz_frame)
        self.spectogram_window.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)
        ax.set_title("Spectogram")
        ax.plot([1, 2, 3, 4, 5, 6, 7])
        self.spectogram_window.draw()
        self.spectogram_ax = ax

        data_viz_freq_control_frame = tk.Frame(data_viz_frame, bd=1, relief=tk.FLAT)
        data_viz_freq_control_frame.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(data_viz_freq_control_frame, text="Upper \nbound (Hz):", anchor=tk.W).grid(row=0, column=0, pady=5, padx=5)
        
        self.data_viz_upper_bound_slider = tk.Scale(data_viz_freq_control_frame, 
                                                    from_=self.data_viz_control.max_upper_freq_bound, 
                                                    to=self.data_viz_control.lower_freq_bound.get(),
                                                      variable=self.data_viz_control.upper_freq_bound,
                                                      orient=tk.VERTICAL, resolution=10, length=200, command=self.on_upper_bound_change,
                                                      width=15)
        self.data_viz_upper_bound_slider.set(self.data_viz_control.upper_freq_bound.get())
        self.data_viz_upper_bound_slider.grid(row=1, column=0, pady=5, padx=5, sticky=tk.E)

        tk.Label(data_viz_freq_control_frame, text="Lower \nbound (Hz):", anchor=tk.W).grid(row=2, column=0, pady=5, padx=5)

        self.data_viz_lower_bound_slider = tk.Scale(data_viz_freq_control_frame, from_=self.data_viz_control.upper_freq_bound.get(), 
                                                    to=self.data_viz_control.min_lower_freq_bound, 
                                                    variable=self.data_viz_control.lower_freq_bound, 
                                                    orient=tk.VERTICAL, resolution=10, length=200, command=self.on_lower_bound_change, 
                                                    width=15)
        self.data_viz_lower_bound_slider.set(self.data_viz_control.lower_freq_bound.get())
        self.data_viz_lower_bound_slider.grid(row=3, column=0, pady=5, padx=5, sticky=tk.E)

        data_viz_v_control_frame = tk.Frame(data_viz_frame, bd=1, relief=tk.FLAT)
        data_viz_v_control_frame.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)

        tk.Label(data_viz_v_control_frame, text="Vmin:", anchor=tk.W).grid(row=0, column=0, pady=5, padx=5)

        self.data_viz_vmin_slider = tk.Scale(data_viz_v_control_frame, from_=self.data_viz_control.min_vmin, to=self.data_viz_control.vmax.get(), variable=self.data_viz_control.vmin,
                                                orient=tk.HORIZONTAL, resolution=5, length=200, command=self.on_vmin_change,
                                                width=10)
        self.data_viz_vmin_slider.set(self.data_viz_control.vmin.get())
        self.data_viz_vmin_slider.grid(row=0, column=1, pady=5, padx=5, sticky=tk.S)

        tk.Label(data_viz_v_control_frame, text="Vmax:", anchor=tk.W).grid(row=0, column=2, pady=5, padx=5)

        self.data_viz_vmax_slider = tk.Scale(data_viz_v_control_frame, from_=self.data_viz_control.vmin.get(), to=self.data_viz_control.max_vmax, variable=self.data_viz_control.vmax,
                                                orient=tk.HORIZONTAL, resolution=5, length=200, command=self.on_vmax_change,
                                                width=10)
        self.data_viz_vmax_slider.set(self.data_viz_control.vmax.get())
        self.data_viz_vmax_slider.grid(row=0, column=3, pady=5, padx=5, sticky=tk.S)

        data_viz_sample_size_frame = tk.Frame(data_viz_frame, bd=1, relief=tk.FLAT)
        data_viz_sample_size_frame.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)

        tk.Label(data_viz_sample_size_frame, text="Sample size:", anchor=tk.W).grid(row=0, column=0, pady=5, padx=5)

        self.data_viz_sample_size_slider = tk.Scale(data_viz_sample_size_frame, from_=self.data_viz_control.min_max_sample_size, to=self.data_viz_control.max_max_sample_size, variable=self.data_viz_control.sample_size,
                                                orient=tk.HORIZONTAL, resolution=self.data_viz_control.sample_size_step, length=200,
                                                width=10)
        self.data_viz_sample_size_slider.set(self.data_viz_control.sample_size.get())
        self.data_viz_sample_size_slider.grid(row=0, column=1, pady=5, padx=5, sticky=tk.S)

        tk.Label(data_viz_sample_size_frame, text="Sample available:", anchor=tk.W).grid(row=0, column=2, pady=5, padx=5)

        self.data_viz_sample_available_label = tk.Label(data_viz_sample_size_frame, text="0", anchor=tk.W)
        self.data_viz_sample_available_label.grid(row=0, column=3, pady=5, padx=5)

    def create_system_control_widget(self):
        system_control_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        system_control_frame.grid(row=1, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(system_control_frame, text="Commands").grid(row=0, column=0, columnspan=3)

        self.override_status_label = tk.Label(system_control_frame, text="Override Status: OFF")
        self.override_status_label.grid(row=1, column=0, pady=5)
        self.override_toggle = tk.Button(system_control_frame, text="Turn ON", command=self.toggle_override)
        self.override_toggle.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(system_control_frame, text="Clock on boot:").grid(row=2, column=0, pady=5)

        self.clock_on_boot_label = tk.Label(system_control_frame, text="--")
        self.clock_on_boot_label.grid(row=2, column=1, pady=5)

        tk.Label(system_control_frame, text="CPU clock:").grid(row=3, column=0, pady=5)

        self.cpu_clock_label = tk.Label(system_control_frame, text="--")
        self.cpu_clock_label.grid(row=3, column=1, pady=5)

        tk.Label(system_control_frame, text="Config clock:").grid(row=4, column=0, pady=5)

        self.config_clock_label = tk.Label(system_control_frame, text="--")
        self.config_clock_label.grid(row=4, column=1, pady=5)

        tk.Button(system_control_frame, text="Config CPU clock (MHz)", command=self.set_cpu_clock).grid(row=5, column=0, pady=5, padx=5)
        self.system_control_data.config_cpu_clock = tk.IntVar()
        self.cpu_clock_slider = tk.Scale(system_control_frame, from_=600, to=2200, variable=self.system_control_data.config_cpu_clock, orient=tk.HORIZONTAL, resolution=100)
        self.cpu_clock_slider.grid(row=5, column=1, pady=5, padx=5)

        tk.Button(system_control_frame, text="Reboot RPI" , command=self.reboot_rpi).grid(row=6, column=0, pady=5, padx=5)

    def create_temperature_control_widget(self):
        # Section that shows temperature and fan speed
        sensor_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        sensor_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.N)
        tk.Label(sensor_frame, text="Temperature control").grid(row=0, column=0, columnspan=2)

        box_temp_frame = tk.Frame(sensor_frame, bd=1, relief=tk.FLAT)
        box_temp_frame.grid(row=1, column=0, pady=5, padx=5)
        tk.Label(box_temp_frame, text="Box", font='Segoe 9 bold').grid(row=0, column=0)

        box_temperature_frame = tk.Frame(box_temp_frame, bd=1, relief=tk.GROOVE)
        box_temperature_frame.grid(row=1, column=0, pady=5, padx=5)
        tk.Label(box_temperature_frame, text="Box temp:", width=8, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.box_temperature_label = tk.Label(box_temperature_frame, text="--", width=5, anchor=tk.W)
        self.box_temperature_label.grid(row=0, column=1, pady=5)

        box_fan_frame = tk.Frame(box_temp_frame, bd=1, relief=tk.GROOVE)
        box_fan_frame.grid(row=2, column=0, pady=5, padx=5)
        tk.Label(box_fan_frame, text="Box fan:", width=8, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.box_fan_label = tk.Label(box_fan_frame, text="--", width=4)
        self.box_fan_label.grid(row=0, column=1, pady=5, padx=3.25)

        self.box_fan_toggle = tk.Button(box_temp_frame, text="Turn ON", command=self.toggle_box_fans)
        self.box_fan_toggle.grid(row=3, column=0, pady=5, padx=5)

        rpi_temp_frame = tk.Frame(sensor_frame, bd=1, relief=tk.FLAT)
        rpi_temp_frame.grid(row=1, column=1, pady=5, padx=5)
        tk.Label(rpi_temp_frame, text="RPi", font='Segoe 9 bold').grid(row=0, column=0)

        cpu_temperature_frame = tk.Frame(rpi_temp_frame, bd=1, relief=tk.GROOVE)
        cpu_temperature_frame.grid(row=1, column=0, pady=5, padx=5)
        tk.Label(cpu_temperature_frame, text="CPU temp:").grid(row=0, column=0, pady=5)
        self.cpu_temperature_label = tk.Label(cpu_temperature_frame, text="--", width=5, anchor=tk.W)
        self.cpu_temperature_label.grid(row=0, column=1, pady=5)

        rpi_fan_frame = tk.Frame(rpi_temp_frame, bd=1, relief=tk.GROOVE)
        rpi_fan_frame.grid(row=2, column=0, pady=5, padx=5)
        tk.Label(rpi_fan_frame, text="RPi fan:", width=8, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.rpi_fan_label = tk.Label(rpi_fan_frame, text="--", width=4)
        self.rpi_fan_label.grid(row=0, column=1, pady=5, padx=3.25)

        self.rpi_fan_toggle = tk.Button(rpi_temp_frame, text="Turn ON", command=self.toggle_rpi_fans)
        self.rpi_fan_toggle.grid(row=3, column=0, pady=5, padx=5)

    def create_gps_widget(self):
        # Section for gps data
        gps_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        gps_frame.grid(row=2, column=1, padx=10, pady=10, sticky=tk.N)
        tk.Label(gps_frame, text="GPS Data").grid(row=0, column=0, columnspan=2)

        gps_latitude_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_latitude_frame.grid(row=1, column=0, pady=5, padx=5)
        tk.Label(gps_latitude_frame, text="Lat:", width=5, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.gps_latitude_label = tk.Label(gps_latitude_frame, width=10, anchor=tk.W)
        self.gps_latitude_label.grid(row=0, column=1, pady=5)

        gps_longitude_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_longitude_frame.grid(row=1, column=1, pady=5, padx=5)
        tk.Label(gps_longitude_frame, text="Lon:", width=5, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.gps_longitude_label = tk.Label(gps_longitude_frame, width=10, anchor=tk.W)
        self.gps_longitude_label.grid(row=0, column=1, pady=5)

        gps_altitude_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_altitude_frame.grid(row=2, column=0, pady=5, padx=5)
        tk.Label(gps_altitude_frame, text="Alt:", width=5, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.gps_altitude_label = tk.Label(gps_altitude_frame, width=10, anchor=tk.W)
        self.gps_altitude_label.grid(row=0, column=1, pady=5)

        gps_error_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_error_frame.grid(row=2, column=1, pady=5, padx=5)
        tk.Label(gps_error_frame, text="Error:", width=5, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.gps_error_label = tk.Label(gps_error_frame, width=10, anchor=tk.W)
        self.gps_error_label.grid(row=0, column=1, pady=5)

        gps_speed_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_speed_frame.grid(row=3, column=0, pady=5, padx=5)
        tk.Label(gps_speed_frame, text="Speed:", width=5, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.gps_speed_label = tk.Label(gps_speed_frame, width=10, anchor=tk.W)
        self.gps_speed_label.grid(row=0, column=1, pady=5)

        gps_climb_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_climb_frame.grid(row=3, column=1, pady=5, padx=5)
        tk.Label(gps_climb_frame, text="Climb:", width=5, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.gps_climb_label = tk.Label(gps_climb_frame, width=10, anchor=tk.W)
        self.gps_climb_label.grid(row=0, column=1, pady=5)

        gps_time_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_time_frame.grid(row=4, column=0, pady=5, padx=5)
        tk.Label(gps_time_frame, text="Time:", width=5, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.gps_time_label = tk.Label(gps_time_frame, width=10, anchor=tk.W)
        self.gps_time_label.grid(row=0, column=1, pady=5)

        gps_track_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_track_frame.grid(row=4, column=1, pady=5, padx=5)
        tk.Label(gps_track_frame, text="Track:", width=5, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.gps_track_label = tk.Label(gps_track_frame, width=10, anchor=tk.W)
        self.gps_track_label.grid(row=0, column=1, pady=5)

        gps_satellites_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_satellites_frame.grid(row=5, column=0, pady=5, padx=5, columnspan=2)
        tk.Label(gps_satellites_frame, text="Satellites:", width=7, anchor=tk.W).grid(row=0, column=0, pady=5)
        self.gps_satellites_label = tk.Label(gps_satellites_frame, width=27, anchor=tk.W)
        self.gps_satellites_label.grid(row=0, column=1, pady=5)

    def create_received_sequence_status_widget(self):
        # Section that shows raw data received
        raw_data_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID)
        raw_data_frame.grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
        tk.Label(raw_data_frame, text="Samples received").grid(row=0, column=0)
    
        self.rcv_data_label = tk.Label(raw_data_frame, text="0", width=45, anchor=tk.W,relief=tk.SUNKEN, bg="white")
        self.rcv_data_label.grid(row=1, column=0, pady=5)

        date_time_frame = tk.Frame(raw_data_frame, bd=1)
        date_time_frame.grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)

    
        tk.Label(date_time_frame, text="Time:", anchor=tk.W ).grid(row=0, column=0, pady=2)

        self.received_time_label = tk.Label(date_time_frame, text='-----', anchor=tk.W)
        self.received_time_label.grid(row=0, column=1, pady=2)

    def create_widgets(self):

        self.create_server_status_widget()
        self.create_data_spec_widget()
        self.create_system_control_widget()
        self.create_temperature_control_widget()
        self.create_gps_widget()
        self.create_received_sequence_status_widget()

    def on_lower_bound_change(self, value):
        # Function to handle lower bound value changes
        self.data_viz_upper_bound_slider.config(to=self.data_viz_lower_bound_slider.get())

    def on_upper_bound_change(self, value):
        # Function to handle upper bound value changes
        self.data_viz_lower_bound_slider.config(from_=self.data_viz_upper_bound_slider.get())

    def on_vmin_change(self, value):
        # Function to handle vmin value changes
        self.data_viz_vmax_slider.config(from_=self.data_viz_vmin_slider.get())

    def on_vmax_change(self, value):
        # Function to handle vmax value changes
        self.data_viz_vmin_slider.config(to=self.data_viz_vmax_slider.get())

    # Button/action functions

    def toggle_override(self):
        print("LOG: Toggle override button pressed")
        if self.system_control_data.override_mode == True:
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
        self.send_cpu_clock(self.system_control_data.config_cpu_clock.get())

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
            "type": "OS",
            "action": "OVERRIDE",
            "value": True	
        })

    def send_override_off(self):
        print("LOG: Override off button pressed")
        self.send_command({
            "type": "OS",
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

    def int_to_scientific_notation(self, integer):
        scientific_str = "{:.2e}".format(integer)
        return scientific_str

    def draw_spectogram(self):

        PM_START = time.time()

        if not self.received_samples:
            return
        
        data_len = len(self.received_samples)

        sample_size = self.data_viz_control.sample_size.get()

        if data_len > sample_size:
            display_data = list(zip(*self.received_samples))[0][data_len-int(sample_size):]
        else:
            display_data = list(zip(*self.received_samples))[0]

        ylim = [self.data_viz_control.lower_freq_bound.get(), self.data_viz_control.upper_freq_bound.get()]
        vmin = self.data_viz_control.vmin.get()
        vmax = self.data_viz_control.vmax.get()

        self.spectogram_ax.clear()
        self.spectogram_ax.specgram(display_data, Fs=1600, vmin=vmin, vmax=vmax)
        self.spectogram_ax.set_ylim(ylim)
        self.spectogram_window.draw()

        self.performance_recordings.record("update_spectogram", time.time() - PM_START)

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

        PM_START = time.time()

        self.received_sample_clusters.append(data)
        self.received_samples.extend(data)

        data_len = len(self.received_samples)

        sample_size = self.data_viz_control.max_max_sample_size

        if data_len > sample_size:
            self.received_samples = self.received_samples[data_len-int(sample_size):]

        if len(self.received_sample_clusters) > 20:
            self.received_sample_clusters.pop(0)

        display_data_sizes = [len(d) for d in self.received_sample_clusters]

        self.rcv_data_label.config(text=display_data_sizes[::-1])

        self.received_time_label.config(text=datetime.now().strftime("%H:%M:%S"))

        self.performance_recordings.record("update_sensor_data", time.time()-PM_START)

    def update_temperature_status_frame(self):
        # Function to update temperature label
        self.box_temperature_label.config(text=str(self.temperature_status.box_temperature))
        self.cpu_temperature_label.config(text=str(self.temperature_status.cpu_temperature))

        self.box_fan_label.config(text="ON" if self.temperature_status.box_fan else "OFF", bg="green" if self.temperature_status.box_fan else "red")
        self.rpi_fan_label.config(text="ON" if self.temperature_status.rpi_fan else "OFF", bg="green" if self.temperature_status.rpi_fan else "red")


        if self.temperature_status.box_fan == True:
            self.box_fan_toggle.config(text="Turn OFF")
        else:
            self.box_fan_toggle.config(text="Turn ON")

        if self.temperature_status.rpi_fan == True:
            self.rpi_fan_toggle.config(text="Turn OFF")
        else:
            self.rpi_fan_toggle.config(text="Turn ON")
        
    def update_gps_status_frame(self):
        # Function to update GPS label
        self.gps_latitude_label.config(text=str(self.gps_status.lat))
        self.gps_longitude_label.config(text=str(self.gps_status.lon))
        self.gps_altitude_label.config(text=str(self.gps_status.alt))
        self.gps_speed_label.config(text=str(self.gps_status.speed))
        self.gps_climb_label.config(text=str(self.gps_status.climb))
        self.gps_track_label.config(text=str(self.gps_status.track))
        self.gps_time_label.config(text=str(self.gps_status.time))
        self.gps_error_label.config(text=str(self.gps_status.error))
        self.gps_satellites_label.config(text=str(self.gps_status.satellites))

    def update_system_control(self):

        if self.system_control_data.override_mode == True:
            self.override_toggle.config(text="Turn OFF")
        else:
            self.override_toggle.config(text="Turn ON")

        self.override_status_label.config(text="Override Status: " + ("ON" if self.system_control_data.override_mode else "OFF"))
        
        self.clock_on_boot_label.config(text=self.system_control_data.clock_on_boot)

        self.cpu_clock_label.config(text=self.system_control_data.current_cpu_clock)

        self.config_clock_label.config(text=self.system_control_data.clock_config)


    async def update_spectogram_task(self):
        while True:
            self.draw_spectogram()
            await asyncio.sleep(1)

    async def update_task(self):
        while True:
            self.update_real_time_data()
            self.update_temperature_status_frame()
            self.update_system_control()
            self.update_server_status()
            self.update_gps_status_frame()
            await asyncio.sleep(UPDATE_UI_INTERVAL)

    def set_temperature_status(self, data):
        self.temperature_status.cpu_temperature = round(data["cpu_temperature"], 2)
        self.temperature_status.box_temperature = round(data["box_temperature"], 2)
        self.temperature_status.box_fan = data["box_fan"]
        self.temperature_status.rpi_fan = data["rpi_fan"]
        

    def set_system_control_data(self, data):
        self.system_control_data.override_mode = data["override_mode"]
        self.system_control_data.clock_on_boot = data["clock_on_boot"]
        self.system_control_data.current_cpu_clock = data["cpu_speed"]
        self.system_control_data.clock_config = data["clock_config"]
    
    def set_gps_status(self, data):
        self.gps_status.lat = data["lat"]
        self.gps_status.lon = data["lon"]
        self.gps_status.alt = data["alt"]
        self.gps_status.speed = data["speed"]
        self.gps_status.climb = data["climb"]
        self.gps_status.satellites = data["satellites"]
        self.gps_status.time = data["time"]
        self.gps_status.error = data["error"]
        self.gps_status.track = data["track"]