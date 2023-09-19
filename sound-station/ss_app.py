import asyncio
import json
import tkinter as tk
from datetime import datetime
from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from app_models import DataVizControl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from position_def import open_position_def
from target_def import open_target_def

SUB_DISTANCE = 2.55
UPDATE_UI_INTERVAL = 1/12

UPDATE_UI_INTERVAL = 1/12
FPS = 24

LABEL_FONT = ("Helvetica", 9)  # You can make this size configurable
TEXT_FONT = ("Helvetica", 8)
PAD_X = 4
PAD_Y = 3
FIG_SIZE = [10, 6]


class SSApp:
    def __init__(self, root, serial_com, data_manager, delay_module, gps_module, settings):
        self.root = root
        self.root.title("Sound Station")
        self.serial_com = serial_com
        self.data_manager = data_manager

        self.received_sample_clusters = []
        self.received_samples = []

        self.gps_module = gps_module
        self.delay_module = delay_module
        self.data_viz_control = DataVizControl()

        global LABEL_FONT, TEXT_FONT, PAD_X, PAD_Y, FIG_SIZE
        LABEL_FONT = settings["label_font"]
        TEXT_FONT = settings["text_font"]
        PAD_X = settings["padx"]
        PAD_Y = settings["pady"]
        FIG_SIZE = settings["fig_size"]

        self.create_widgets()

    def calculate_angle_2_subs(self, frame):

        # TODO hardcoded for now
        sub_distance = SUB_DISTANCE
        delay_sub_0 = self.delay_module.entry_boxes[4].get()
        delay_sub_1 = self.delay_module.entry_boxes[5].get()

        if not delay_sub_0 or not delay_sub_1:
            print("No delay cycles entered")  # TODO log in UI
            return 0

        delay_cycles = int(delay_sub_1) - int(delay_sub_0)
        print("Delay cycles: {}".format(delay_cycles))

        # speed of sound in air
        c = 343.0
        delay_between_tx = 1/1600  # in seconds
        distance_traveled = c * delay_between_tx * delay_cycles

        print("Distance traveled: {} meters".format(distance_traveled))

        transmission_angle = np.rad2deg(
            np.pi/2-np.arctan(distance_traveled/sub_distance))

        # round transmission angle to 4 decimal places
        transmission_angle = round(transmission_angle, 4)

        frame.result_label.config(text="Tx angle: " + str(transmission_angle))

    def get_delay_values(self):
        values = []
        for sub in self.delay_module.subwoofer_array:
            values.append(self.delay_module.subwoofer_array[sub]["delay"])
        return values

    def send_delays(self):

        # value_array = self.convert_entries_to_values(self.delay_module.delay_entries)
        value_array = self.get_delay_values()
        # check if size 6
        if len(value_array) != 6:
            print("Incorrect size of array")
            return

        self.serial_com.send_delays(value_array)

    def toggle_manual_delays(self):
        if self.delay_module.manual_delays_var.get():
            print("Manual control enabled")
            for entry in self.delay_module.delay_entries:
                entry.config(state=tk.NORMAL)
        else:
            print("Manual control disabled")
            for entry in self.delay_module.delay_entries:
                entry.config(state=tk.DISABLED)

    def toggle_manual_send(self):
        if self.delay_module.manual_send_var.get():
            print("Manual send enabled")
            self.send_button.config(state=tk.NORMAL)
        else:
            print("Manual send disabled")
            self.send_button.config(state=tk.DISABLED)

    def toggle_manual_target(self):
        if self.delay_module.manual_target_var.get():
            print("Manual target enabled")
            self.define_targert_button.config(state=tk.NORMAL)
        else:
            print("Manual target disabled")
            self.define_targert_button.config(state=tk.DISABLED)

    def update_serial_monitor(self):
        joined_messages = "\n".join(
            self.serial_com.get_received_messages()[-20::])
        self.text_entry.config(state=tk.NORMAL)
        self.text_entry.delete("1.0", tk.END)
        self.text_entry.insert(tk.END, joined_messages)
        self.text_entry.config(state=tk.DISABLED)

    def update_delay_module(self):
        for i in range(6):

            # label str composed of ned_pos with 2 decimal places

            label_str = "{:.2f}, {:.2f}, {:.2f}".format(self.delay_module.subwoofer_array["sub{}".format(
                i)]["ned_pos"][0], self.delay_module.subwoofer_array["sub{}".format(i)]["ned_pos"][1], self.delay_module.subwoofer_array["sub{}".format(i)]["ned_pos"][2])

            self.ned_labels[i].config(text=label_str)

            if not self.delay_module.manual_delays_var.get():

                self.delay_module.delay_entries[i].config(state=tk.NORMAL)
                self.delay_module.delay_entries[i].delete(0, tk.END)
                self.delay_module.delay_entries[i].insert(
                    0, self.delay_module.subwoofer_array["sub{}".format(i)]["delay"])
                self.delay_module.delay_entries[i].config(state=tk.DISABLED)

    async def update_spectogram_task(self):
        while True:
            self.draw_spectogram()
            await asyncio.sleep(1)

    async def update_task(self):
        while True:
            self.update_serial_monitor()
            self.update_delay_module()
            self.update_gps_status()
            await asyncio.sleep(UPDATE_UI_INTERVAL)

    async def run(self):

        while True:
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

    def create_gps_widget(self):
        # Section for gps data
        gps_frame = tk.Frame(self.section1_frame, bd=1, relief=tk.SOLID)
        gps_frame.grid(row=0, column=0, padx=PAD_X, pady=PAD_Y, sticky=tk.N)
        tk.Label(gps_frame, text="GPS Data", font=LABEL_FONT).grid(
            row=0, column=0, columnspan=2)

        gps_latitude_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_latitude_frame.grid(row=1, column=0, pady=PAD_Y, padx=PAD_X)
        tk.Label(gps_latitude_frame, text="Lat:", width=5, anchor=tk.W,
                 font=LABEL_FONT).grid(row=0, column=0, pady=PAD_Y)
        self.gps_latitude_label = tk.Label(
            gps_latitude_frame, width=10, anchor=tk.W, font=LABEL_FONT)
        self.gps_latitude_label.grid(row=0, column=1, pady=PAD_Y)

        gps_longitude_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_longitude_frame.grid(row=1, column=1, pady=PAD_Y, padx=PAD_X)
        tk.Label(gps_longitude_frame, text="Lon:", width=5, anchor=tk.W,
                 font=LABEL_FONT).grid(row=0, column=0, pady=PAD_Y)
        self.gps_longitude_label = tk.Label(
            gps_longitude_frame, width=10, anchor=tk.W, font=LABEL_FONT)
        self.gps_longitude_label.grid(row=0, column=1, pady=PAD_Y)

        gps_altitude_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_altitude_frame.grid(row=2, column=0, pady=PAD_Y, padx=PAD_X)
        tk.Label(gps_altitude_frame, text="Alt:", width=5, anchor=tk.W,
                 font=LABEL_FONT).grid(row=0, column=0, pady=PAD_Y)
        self.gps_altitude_label = tk.Label(
            gps_altitude_frame, width=10, anchor=tk.W, font=LABEL_FONT)
        self.gps_altitude_label.grid(row=0, column=1, pady=PAD_Y)

        gps_track_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_track_frame.grid(row=2, column=1, pady=PAD_Y, padx=PAD_X)
        tk.Label(gps_track_frame, text="Track:", width=5, anchor=tk.W,
                 font=LABEL_FONT).grid(row=0, column=0, pady=PAD_Y)
        self.gps_track_label = tk.Label(
            gps_track_frame, width=10, anchor=tk.W, font=LABEL_FONT)
        self.gps_track_label.grid(row=0, column=1, pady=PAD_Y)

        gps_speed_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_speed_frame.grid(row=3, column=0, pady=PAD_Y, padx=PAD_X)
        tk.Label(gps_speed_frame, text="Speed:", width=5, anchor=tk.W,
                 font=LABEL_FONT).grid(row=0, column=0, pady=PAD_Y)
        self.gps_speed_label = tk.Label(
            gps_speed_frame, width=10, anchor=tk.W, font=LABEL_FONT)
        self.gps_speed_label.grid(row=0, column=1, pady=PAD_Y)

        gps_climb_frame = tk.Frame(gps_frame, bd=1, relief=tk.GROOVE)
        gps_climb_frame.grid(row=3, column=1, pady=PAD_Y, padx=PAD_X)
        tk.Label(gps_climb_frame, text="Climb:", width=5, anchor=tk.W,
                 font=LABEL_FONT).grid(row=0, column=0, pady=PAD_Y)
        self.gps_climb_label = tk.Label(
            gps_climb_frame, width=10, anchor=tk.W, font=LABEL_FONT)
        self.gps_climb_label.grid(row=0, column=1, pady=PAD_Y)

    def create_delay_widget(self):
        # Section for manual control
        delay_frame = tk.Frame(self.section1_frame, bd=1, relief=tk.SOLID)
        delay_frame.grid(row=1, column=0, padx=PAD_X, pady=PAD_Y)

        title = tk.Label(delay_frame, text="Delay control", font=LABEL_FONT)
        title.grid(row=0, column=0, columnspan=2, padx=PAD_X, pady=PAD_Y)

        pointing_to_frame = tk.Frame(delay_frame, bd=1, relief=tk.GROOVE)
        pointing_to_frame.grid(
            row=1, column=0, padx=PAD_X, pady=PAD_Y, columnspan=2)

        tk.Label(pointing_to_frame, text="Pointing to:", width=12,
                 font=LABEL_FONT).grid(row=1, column=0, padx=10, pady=PAD_Y)
        self.balloon_pos_label = tk.Label(
            pointing_to_frame, text="0, 0, 0", width=26, anchor=tk.W, font=LABEL_FONT)
        self.balloon_pos_label.grid(row=1, column=1, padx=PAD_X, pady=PAD_Y)

        subarray_lla_frame = tk.Frame(delay_frame, bd=1, relief=tk.GROOVE)
        subarray_lla_frame.grid(
            row=2, column=0, padx=PAD_X, pady=PAD_Y, columnspan=2)

        tk.Label(subarray_lla_frame, text="Subarray LLA:", width=12,
                 font=LABEL_FONT).grid(row=1, column=0, padx=10, pady=PAD_Y)
        self.subarray_lla_label = tk.Label(
            subarray_lla_frame, text="0, 0, 0", width=26, anchor=tk.W, font=LABEL_FONT)
        self.subarray_lla_label.grid(row=1, column=1, padx=PAD_X, pady=PAD_Y)

        azimuth_elevation_frame = tk.Frame(delay_frame, bd=1, relief=tk.GROOVE)
        azimuth_elevation_frame.grid(
            row=3, column=0, padx=PAD_X, pady=PAD_Y, columnspan=2)

        azimuth_frame = tk.Frame(azimuth_elevation_frame, bd=1, relief=tk.FLAT)
        azimuth_frame.grid(row=0, column=0, padx=PAD_X)

        tk.Label(azimuth_frame, text="Heading:", width=8, anchor=tk.W,
                 font=LABEL_FONT).grid(row=0, column=0, pady=PAD_Y)
        self.azimuth_label = tk.Label(
            azimuth_frame, text="0", width=10, anchor=tk.W, font=LABEL_FONT)
        self.azimuth_label.grid(row=0, column=1, pady=PAD_Y)

        elevation_frame = tk.Frame(
            azimuth_elevation_frame, bd=1, relief=tk.FLAT)
        elevation_frame.grid(row=0, column=1, padx=PAD_X)

        tk.Label(elevation_frame, text="Elevation:", width=8,
                 anchor=tk.W, font=LABEL_FONT).grid(row=0, column=0, pady=PAD_Y)
        self.elevation_label = tk.Label(
            elevation_frame, text="0", width=10, anchor=tk.W, font=LABEL_FONT)
        self.elevation_label.grid(row=0, column=1, pady=PAD_Y)

        subwoofer_delays_frame = tk.Frame(delay_frame, bd=1, relief=tk.FLAT)
        subwoofer_delays_frame.grid(
            row=4, column=0, padx=PAD_X, pady=PAD_Y, columnspan=2)

        self.delay_module.entry_boxes = []

        self.ned_labels = []

        for i in range(6):

            sub_frame = tk.Frame(subwoofer_delays_frame, bd=1, relief=tk.FLAT)
            sub_frame.grid(row=(i)//2, column=(i) % 2)

            tk.Label(sub_frame, text="Subwoofer " + str(i),
                     font=LABEL_FONT).grid(row=0, column=0, padx=PAD_X, pady=PAD_Y)

            ned_frame = tk.Frame(sub_frame, bd=1, relief=tk.GROOVE)
            ned_frame.grid(row=1, column=0, padx=PAD_X, pady=PAD_Y)

            tk.Label(ned_frame, text="NED pos:", width=8, anchor=tk.W,
                     font=LABEL_FONT).grid(row=0, column=0, pady=PAD_Y)
            ned_label = tk.Label(ned_frame, text="0, 0, 0",
                                 width=12, anchor=tk.W, font=LABEL_FONT)
            ned_label.grid(row=0, column=1, pady=PAD_Y)

            self.ned_labels.append(ned_label)

            sub_delay_frame = tk.Frame(sub_frame, bd=1, relief=tk.GROOVE)
            sub_delay_frame.grid(row=2, column=0, padx=PAD_X, pady=PAD_Y)

            label2 = tk.Label(sub_delay_frame, text="Delay:",
                              width=5, anchor=tk.W, font=LABEL_FONT)
            label2.grid(row=0, column=0, pady=PAD_Y)

            entry = tk.Entry(sub_delay_frame, width=14, font=TEXT_FONT,
                             textvariable=self.delay_module.subwoofer_array["sub{}".format(i)]["delay_tk"], state=tk.DISABLED)
            entry.grid(row=0, column=1, pady=PAD_Y, padx=PAD_X)

            self.delay_module.subwoofer_array["sub{}".format(i)]["delay_tk"].trace(
                "w", self.delay_module.update_delays)

            self.delay_module.delay_entries.append(entry)

        check_manual_send = tk.Checkbutton(
            delay_frame, text="Manual send", variable=self.delay_module.manual_send_var, command=self.toggle_manual_send)
        check_manual_send.grid(row=7, column=0, padx=PAD_X, pady=PAD_Y)

        check_manual_delay = tk.Checkbutton(
            delay_frame, text="Manual target", variable=self.delay_module.manual_target_var, command=self.toggle_manual_target)
        check_manual_delay.grid(row=8, column=0, padx=PAD_X, pady=PAD_Y)

        check_manual_delay = tk.Checkbutton(
            delay_frame, text="Manual delays", variable=self.delay_module.manual_delays_var, command=self.toggle_manual_delays)
        check_manual_delay.grid(row=9, column=0, padx=PAD_X, pady=PAD_Y)

        self.define_pos_button = tk.Button(delay_frame, text="Define positions", font=TEXT_FONT,  width=18, command=partial(
            open_position_def, self.root, self.delay_module))
        self.define_pos_button.grid(row=9, column=1, padx=PAD_X, pady=PAD_Y)

        self.send_button = tk.Button(
            delay_frame, text="Send delays", font=TEXT_FONT, command=self.send_delays, width=18)
        self.send_button.grid(row=7, column=1, padx=PAD_X, pady=PAD_Y)
        self.send_button.config(state=tk.DISABLED)

        self.define_targert_button = tk.Button(delay_frame, text="Define target", font=TEXT_FONT, command=partial(
            open_target_def, self.root, self.delay_module), width=18)
        self.define_targert_button.grid(
            row=8, column=1, padx=PAD_X, pady=PAD_Y)
        self.define_targert_button.config(state=tk.DISABLED)

    def create_log_widget(self):

        logs_frame = tk.Frame(self.root, bd=1, relief=tk.FLAT)
        logs_frame.grid(row=0, column=1, padx=PAD_X, pady=PAD_Y)

        # frame that shows the last 8 messages from the serial_com
        serial_com_frame = tk.Frame(logs_frame, bd=1, relief=tk.FLAT)
        serial_com_frame.grid(row=0, column=0, padx=PAD_X, pady=PAD_Y)

        serial_com_frame_title = tk.Label(
            serial_com_frame, text="Serial Com", font=LABEL_FONT)
        serial_com_frame_title.grid(row=0, column=0, padx=PAD_X, pady=PAD_Y)

        joined_messages = "\n".join(self.serial_com.get_received_messages())
        self.text_entry = tk.Text(
            serial_com_frame, height=20, width=40, font=TEXT_FONT)
        self.text_entry.grid(row=1, column=0, padx=PAD_X, pady=PAD_Y)
        self.text_entry.insert(tk.END, joined_messages)
        self.text_entry.config(state=tk.DISABLED)
        # text_entry.grid(row=0, column=0, padx=10, pady=10)

        # ##### SYSTEM LOGS ##### #

        system_logs_frame = tk.Frame(logs_frame, bd=1, relief=tk.FLAT)
        system_logs_frame.grid(row=1, column=0, padx=PAD_X, pady=PAD_Y)

        # Section that shows raw data received
        raw_data_frame = tk.Frame(system_logs_frame, bd=1, relief=tk.FLAT)
        raw_data_frame.grid(row=2, column=0, padx=PAD_X, pady=PAD_Y)

        tk.Label(raw_data_frame, text="Raw data received",
                 font=LABEL_FONT).grid(row=0, column=0)
        self.rcv_data_label = tk.Label(
            raw_data_frame, text="0", width=45, anchor=tk.W, relief=tk.SUNKEN, bg="white", font=LABEL_FONT)
        self.rcv_data_label.grid(row=1, column=0, pady=PAD_Y)

    def create_data_spec_widget(self):
        # Section shows plot of data received

        self.data_viz_frame = tk.Frame(self.root, bd=1, relief=tk.FLAT)
        data_viz_frame = self.data_viz_frame
        data_viz_frame.grid(row=0, column=2, padx=PAD_X, pady=PAD_Y, rowspan=4)

        self.fig_single_sensor, self.ax_single_sensor = plt.subplots(
            1, 1, figsize=FIG_SIZE, dpi=50)
        ax = self.ax_single_sensor
        ax.text(
            0.5, 0.5, "No data",
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes,
            fontsize=20,  # Set the fontsize here
        )
        ax.xaxis.set_visible(False)

        plt.tight_layout()

        self.fig_all_sensor, self.axs_all_sensors = plt.subplots(
            2, 2, figsize=(20, 12), dpi=50)
        i = 0
        for axs_row in self.axs_all_sensors:
            for ax in axs_row:
                ax.text(
                    0.5, 0.5, "No data",
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=ax.transAxes,
                    fontsize=20,  # Set the fontsize here
                )
                ax.title.set_text("Sensor " + str(i))

                ax.xaxis.set_visible(False)
                if i == 1 or i == 3:
                    ax.yaxis.set_visible(False)
                i += 1
        plt.tight_layout()

        self.spectogram_window = FigureCanvasTkAgg(
            self.fig_single_sensor, data_viz_frame)
        self.spectogram_window.get_tk_widget().grid(row=0, column=0)
        self.spectogram_window.draw()

        data_viz_control_frame = tk.Frame(
            data_viz_frame, bd=1, relief=tk.SOLID)
        data_viz_control_frame.grid(
            row=0, column=1, pady=PAD_Y, padx=PAD_X, rowspan=3)

        drop = tk.OptionMenu(data_viz_control_frame, self.data_viz_control.selected_spec_mode,
                             *self.data_viz_control.select_spec_options)
        drop.grid(row=0, column=0, pady=PAD_Y, padx=PAD_X)
        self.data_viz_control.selected_spec_mode.trace(
            "w", self.on_spec_mode_change)

        tk.Label(data_viz_control_frame, text="Upper \nbound (Hz):", anchor=tk.W,
                 font=LABEL_FONT).grid(row=1, column=0, pady=5, padx=PAD_X)

        self.data_viz_upper_bound_slider = tk.Scale(data_viz_control_frame,
                                                    from_=self.data_viz_control.max_upper_freq_bound,
                                                    to=self.data_viz_control.lower_freq_bound.get(),
                                                    variable=self.data_viz_control.upper_freq_bound,
                                                    orient=tk.VERTICAL, resolution=10, length=200, command=self.on_upper_bound_change,
                                                    width=15)
        self.data_viz_upper_bound_slider.set(
            self.data_viz_control.upper_freq_bound.get())
        self.data_viz_upper_bound_slider.grid(
            row=2, column=0, pady=PAD_Y, padx=PAD_X, sticky=tk.E)

        tk.Label(data_viz_control_frame, text="Lower \nbound (Hz):", anchor=tk.W,
                 font=LABEL_FONT).grid(row=3, column=0, pady=5, padx=PAD_X)

        self.data_viz_lower_bound_slider = tk.Scale(data_viz_control_frame, from_=self.data_viz_control.upper_freq_bound.get(),
                                                    to=self.data_viz_control.min_lower_freq_bound,
                                                    variable=self.data_viz_control.lower_freq_bound,
                                                    orient=tk.VERTICAL, resolution=10, length=200, command=self.on_lower_bound_change,
                                                    width=15)
        self.data_viz_lower_bound_slider.set(
            self.data_viz_control.lower_freq_bound.get())
        self.data_viz_lower_bound_slider.grid(
            row=4, column=0, pady=PAD_Y, padx=PAD_X, sticky=tk.E)

        data_viz_v_control_frame = tk.Frame(
            data_viz_frame, bd=1, relief=tk.FLAT)
        data_viz_v_control_frame.grid(
            row=1, column=0, pady=PAD_Y, padx=PAD_X, sticky=tk.W)

        tk.Label(data_viz_v_control_frame, text="Vmin:", anchor=tk.W,
                 font=LABEL_FONT).grid(row=0, column=0, pady=PAD_Y, padx=PAD_X)

        self.data_viz_vmin_slider = tk.Scale(data_viz_v_control_frame, from_=self.data_viz_control.min_vmin, to=self.data_viz_control.vmax.get(), variable=self.data_viz_control.vmin,
                                             orient=tk.HORIZONTAL, resolution=5, length=200, command=self.on_vmin_change,
                                             width=10)
        self.data_viz_vmin_slider.set(self.data_viz_control.vmin.get())
        self.data_viz_vmin_slider.grid(
            row=0, column=1, pady=PAD_Y, padx=PAD_X, sticky=tk.S)

        tk.Label(data_viz_v_control_frame, text="Vmax:", anchor=tk.W,
                 font=LABEL_FONT).grid(row=0, column=2, pady=PAD_Y, padx=PAD_X)

        self.data_viz_vmax_slider = tk.Scale(data_viz_v_control_frame, from_=self.data_viz_control.vmin.get(), to=self.data_viz_control.max_vmax, variable=self.data_viz_control.vmax,
                                             orient=tk.HORIZONTAL, resolution=5, length=200, command=self.on_vmax_change,
                                             width=10)
        self.data_viz_vmax_slider.set(self.data_viz_control.vmax.get())
        self.data_viz_vmax_slider.grid(
            row=0, column=3, pady=PAD_Y, padx=PAD_X, sticky=tk.S)

        data_viz_sample_size_frame = tk.Frame(
            data_viz_frame, bd=1, relief=tk.FLAT)
        data_viz_sample_size_frame.grid(
            row=2, column=0, pady=PAD_Y, padx=PAD_X, sticky=tk.W)

        tk.Label(data_viz_sample_size_frame, text="Sample size:", anchor=tk.W,
                 font=LABEL_FONT).grid(row=0, column=0, pady=PAD_Y, padx=PAD_X)

        self.data_viz_sample_size_slider = tk.Scale(data_viz_sample_size_frame, from_=self.data_viz_control.min_max_sample_size, to=self.data_viz_control.max_max_sample_size, variable=self.data_viz_control.sample_size,
                                                    orient=tk.HORIZONTAL, resolution=self.data_viz_control.sample_size_step, length=200,
                                                    width=10)
        self.data_viz_sample_size_slider.set(
            self.data_viz_control.sample_size.get())
        self.data_viz_sample_size_slider.grid(
            row=0, column=1, pady=PAD_Y, padx=PAD_X, sticky=tk.S)

        tk.Label(data_viz_sample_size_frame, text="Sample available:", anchor=tk.W,
                 font=LABEL_FONT).grid(row=0, column=2, pady=PAD_Y, padx=PAD_X)

        self.data_viz_sample_available_label = tk.Label(
            data_viz_sample_size_frame, text="0", anchor=tk.W, font=LABEL_FONT)
        self.data_viz_sample_available_label.grid(
            row=0, column=3, pady=PAD_Y, padx=PAD_X)

    def create_widgets(self):

        self.section1_frame = tk.Frame(self.root, bd=1, relief=tk.FLAT)
        self.section1_frame.grid(
            row=0, column=0, padx=PAD_X, pady=PAD_Y, sticky=tk.N)

        self.create_gps_widget()
        self.create_delay_widget()
        self.create_log_widget()
        self.create_data_spec_widget()

        self.root.update()

    def on_lower_bound_change(self, value):
        # Function to handle lower bound value changes
        self.data_viz_upper_bound_slider.config(
            to=self.data_viz_lower_bound_slider.get())

    def on_upper_bound_change(self, value):
        # Function to handle upper bound value changes
        self.data_viz_lower_bound_slider.config(
            from_=self.data_viz_upper_bound_slider.get())

    def on_vmin_change(self, value):
        # Function to handle vmin value changes
        self.data_viz_vmax_slider.config(from_=self.data_viz_vmin_slider.get())

    def on_vmax_change(self, value):
        # Function to handle vmax value changes
        self.data_viz_vmin_slider.config(to=self.data_viz_vmax_slider.get())

    def on_spec_mode_change(self, *args):
        print("LOG: Spectogram mode changed to " +
              self.data_viz_control.selected_spec_mode.get())

        if self.data_viz_control.selected_spec_mode.get() == "All Sensors":
            self.spectogram_window.get_tk_widget().grid_forget()
            self.spectogram_window = FigureCanvasTkAgg(
                self.fig_all_sensor, self.data_viz_frame)
            self.spectogram_window.get_tk_widget().grid(row=0, column=0)
            self.draw_spectogram()
        else:
            self.spectogram_window.get_tk_widget().grid_forget()
            self.spectogram_window = FigureCanvasTkAgg(
                self.fig_single_sensor, self.data_viz_frame)
            self.spectogram_window.get_tk_widget().grid(row=0, column=0)
            self.draw_spectogram()

    def draw_spectogram(self):

        if not self.received_samples:
            return

        ylim = [self.data_viz_control.lower_freq_bound.get(
        ), self.data_viz_control.upper_freq_bound.get()]
        vmin = self.data_viz_control.vmin.get()
        vmax = self.data_viz_control.vmax.get()

        data_len = len(self.received_samples)
        sample_size = self.data_viz_control.sample_size.get()
        sensor_id = 0

        if self.data_viz_control.selected_spec_mode.get().startswith("Sensor"):
            sensor_id = int(
                self.data_viz_control.selected_spec_mode.get().split(" ")[1])

            if data_len > sample_size:
                display_data = list(zip(*self.received_samples)
                                    )[sensor_id][data_len-int(sample_size):]
            else:
                display_data = list(zip(*self.received_samples))[sensor_id]

            self.ax_single_sensor.clear()
            self.ax_single_sensor.specgram(
                display_data, Fs=1600, vmin=vmin, vmax=vmax)
            self.ax_single_sensor.set_ylim(ylim)
            self.spectogram_window.draw()

        else:

            display_data = []

            if data_len > sample_size:
                display_data = [list(zip(*self.received_samples))[i]
                                [data_len-int(sample_size):] for i in range(0, 4)]
            else:
                display_data = list(zip(*self.received_samples))

            for i in range(0, 4):

                ax = self.axs_all_sensors[i//2][i % 2]
                ax.clear()
                ax.title.set_text("Sensor " + str(i))
                ax.specgram(display_data[i], Fs=1600, vmin=vmin, vmax=vmax)
                ax.set_ylim(ylim)

            self.spectogram_window.draw()

    def update_data(self, data):
        # Function to update raw data label

        self.received_sample_clusters.append(data)
        self.received_samples.extend(data)

        data_len = len(self.received_samples)

        sample_size = self.data_viz_control.max_max_sample_size

        if data_len > sample_size:
            self.received_samples = self.received_samples[data_len-int(
                sample_size):]

        if len(self.received_sample_clusters) > 20:
            self.received_sample_clusters.pop(0)

        display_data_sizes = [len(d) for d in self.received_sample_clusters]

        self.rcv_data_label.config(text=display_data_sizes[::-1])

    def update_gps_status(self):
        # Function to update GPS label
        self.gps_latitude_label.config(text=str(self.gps_module.latitude))
        self.gps_longitude_label.config(text=str(self.gps_module.longitude))
        self.gps_altitude_label.config(text=str(self.gps_module.altitude))
        self.gps_track_label.config(text=str(self.gps_module.track))
        self.gps_speed_label.config(text=str(self.gps_module.speed))
        self.gps_climb_label.config(text=str(self.gps_module.climb))
        self.balloon_pos_label.config(text="{:.6f}, {:.6f}, {:.6f}".format(
            self.delay_module.balloon_lla_pos['lat'], self.delay_module.balloon_lla_pos['lon'], self.delay_module.balloon_lla_pos['alt']))
        self.subarray_lla_label.config(text="{:.6f}, {:.6f}, {:.6f}".format(
            self.delay_module.subarray_lla_pos['lat'], self.delay_module.subarray_lla_pos['lon'], self.delay_module.subarray_lla_pos['alt']))
        self.azimuth_label.config(
            text="{:.3f}".format(self.delay_module.azimuth))
        self.elevation_label.config(
            text="{:.3f}".format(self.delay_module.elevation))
