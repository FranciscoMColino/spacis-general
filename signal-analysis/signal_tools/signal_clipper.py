import sys
import tkinter as tk
from functools import partial

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .signal_tools_utils import zoom_factory


class DataVizControl:
    def __init__(self):

        self.select_spec_options = [
            "Sensor 0",
            "Sensor 1",
            "Sensor 2",
            "Sensor 3",
            "All Sensors",
        ]
        # self.all_sensors_mode = False

        self.selected_spec_mode = tk.StringVar()
        self.selected_spec_mode.set(self.select_spec_options[0])

        self.min_lower_ylim = 0
        self.max_upper_ylim = 400

        self.min_lower_xlim = 0
        self.max_upper_xlim = 2 ^ 32 - 1

        self.xlim = [self.min_lower_xlim, self.max_upper_xlim]

        self.lower_ylim = tk.IntVar()
        self.lower_ylim.set(0)
        self.upper_ylim = tk.IntVar()
        self.upper_ylim.set(200)

        self.min_vmin = -100
        self.max_vmax = 300

        self.vmin = tk.IntVar()
        self.vmin.set(-10)
        self.vmax = tk.IntVar()
        self.vmax.set(10)

        self.max_max_sample_size = 65536  # pow(2, 12) * 16
        self.min_max_sample_size = 4096  # pow(2, 12) * 1
        self.sample_size_step = 1024  # pow(2, 12) / 4

        self.sample_size = tk.IntVar()
        self.sample_size.set(16384)

        self.timeline_offset = tk.IntVar()
        self.timeline_offset.set(0)


class SignalClipper():
    def __init__(self, root, display_data, sample_freq):
        self.data_viz_control = DataVizControl()
        self.root = root
        self.display_data = display_data
        self.sample_freq = sample_freq
        self.data_viz_control.max_upper_xlim = len(display_data)/800
        self.data_viz_control.xlim = [0, self.data_viz_control.max_upper_xlim]
        self.create_data_spec_widget()

    def create_data_spec_widget(self):
        # Section shows plot of data received

        self.data_viz_frame = tk.Frame(self.root, bd=1, relief=tk.FLAT)
        data_viz_frame = self.data_viz_frame
        data_viz_frame.grid(row=1, column=2, padx=10, pady=10, rowspan=4)

        self.fig, self.ax = plt.subplots(
            1, 1, figsize=(20, 12), dpi=50)
        ax = self.ax
        ax.text(
            0.5, 0.5, "No data",
            horizontalalignment='center',
            verticalalignment='center',
            transform=ax.transAxes,
            fontsize=20,  # Set the fontsize here
        )
        ax.xaxis.set_visible(False)

        self.f = zoom_factory(ax, self.data_viz_control, base_scale=1.1)

        plt.tight_layout()

        self.spectogram_window = FigureCanvasTkAgg(
            self.fig, data_viz_frame)
        self.spectogram_window.get_tk_widget().grid(row=0, column=0)
        self.spectogram_window.draw()

        data_viz_control_frame = tk.Frame(
            data_viz_frame, bd=1, relief=tk.SOLID)
        data_viz_control_frame.grid(row=0, column=1, pady=5, padx=5, rowspan=3)

        tk.Label(data_viz_control_frame, text="Upper \nbound (Hz):",
                 anchor=tk.W).grid(row=1, column=0, pady=5, padx=5)

        self.data_viz_upper_bound_slider = tk.Scale(data_viz_control_frame,
                                                    from_=self.data_viz_control.max_upper_ylim,
                                                    to=self.data_viz_control.lower_ylim.get(),
                                                    variable=self.data_viz_control.upper_ylim,
                                                    orient=tk.VERTICAL, resolution=10, length=200, command=self.on_upper_bound_change,
                                                    width=15)
        self.data_viz_upper_bound_slider.set(
            self.data_viz_control.upper_ylim.get())
        self.data_viz_upper_bound_slider.grid(
            row=2, column=0, pady=5, padx=5, sticky=tk.E)

        tk.Label(data_viz_control_frame, text="Lower \nbound (Hz):",
                 anchor=tk.W).grid(row=3, column=0, pady=5, padx=5)

        self.data_viz_lower_bound_slider = tk.Scale(data_viz_control_frame,
                                                    from_=self.data_viz_control.upper_ylim.get(),
                                                    to=self.data_viz_control.min_lower_ylim,
                                                    variable=self.data_viz_control.lower_ylim,
                                                    orient=tk.VERTICAL, resolution=10, length=200, command=self.on_lower_bound_change,
                                                    width=15)
        self.data_viz_lower_bound_slider.set(
            self.data_viz_control.lower_ylim.get())
        self.data_viz_lower_bound_slider.grid(
            row=4, column=0, pady=5, padx=5, sticky=tk.E)

        data_viz_v_control_frame = tk.Frame(
            data_viz_frame, bd=1, relief=tk.FLAT)
        data_viz_v_control_frame.grid(
            row=1, column=0, pady=5, padx=5, sticky=tk.W)

        tk.Label(data_viz_v_control_frame, text="Vmin:",
                 anchor=tk.W).grid(row=0, column=0, pady=5, padx=5)

        self.data_viz_vmin_slider = tk.Scale(data_viz_v_control_frame, from_=self.data_viz_control.min_vmin, to=self.data_viz_control.vmax.get(), variable=self.data_viz_control.vmin,
                                             orient=tk.HORIZONTAL, resolution=5, length=200, command=self.on_vmin_change,
                                             width=10)
        self.data_viz_vmin_slider.set(self.data_viz_control.vmin.get())
        self.data_viz_vmin_slider.grid(
            row=0, column=1, pady=5, padx=5, sticky=tk.S)

        tk.Label(data_viz_v_control_frame, text="Vmax:",
                 anchor=tk.W).grid(row=0, column=2, pady=5, padx=5)

        self.data_viz_vmax_slider = tk.Scale(data_viz_v_control_frame, from_=self.data_viz_control.vmin.get(), to=self.data_viz_control.max_vmax, variable=self.data_viz_control.vmax,
                                             orient=tk.HORIZONTAL, resolution=5, length=200, command=self.on_vmax_change,
                                             width=10)
        self.data_viz_vmax_slider.set(self.data_viz_control.vmax.get())
        self.data_viz_vmax_slider.grid(
            row=0, column=3, pady=5, padx=5, sticky=tk.S)

        data_viz_sample_size_frame = tk.Frame(
            data_viz_frame, bd=1, relief=tk.FLAT)
        data_viz_sample_size_frame.grid(
            row=2, column=0, pady=5, padx=5, sticky=tk.W)

        tk.Label(data_viz_sample_size_frame, text="Sample size:",
                 anchor=tk.W).grid(row=0, column=0, pady=5, padx=5)

        self.data_viz_sample_size_slider = tk.Scale(data_viz_sample_size_frame, from_=self.data_viz_control.min_max_sample_size, to=self.data_viz_control.max_max_sample_size, variable=self.data_viz_control.sample_size,
                                                    orient=tk.HORIZONTAL, resolution=self.data_viz_control.sample_size_step, length=200,
                                                    width=10)
        self.data_viz_sample_size_slider.set(
            self.data_viz_control.sample_size.get())
        self.data_viz_sample_size_slider.grid(
            row=0, column=1, pady=5, padx=5, sticky=tk.S)

        tk.Label(data_viz_sample_size_frame, text="Sample available:",
                 anchor=tk.W).grid(row=0, column=2, pady=5, padx=5)

        self.data_viz_sample_available_label = tk.Label(
            data_viz_sample_size_frame, text="0", anchor=tk.W)
        self.data_viz_sample_available_label.grid(
            row=0, column=3, pady=5, padx=5)

    def draw_spectogram(self):

        display_data = self.display_data
        sample_freq = self.sample_freq

        ylim = [self.data_viz_control.lower_ylim.get(
        ), self.data_viz_control.upper_ylim.get()]

        vmin = self.data_viz_control.vmin.get()
        vmax = self.data_viz_control.vmax.get()

        self.ax.clear()
        self.ax.specgram(
            display_data, Fs=sample_freq, vmin=vmin, vmax=vmax)
        self.ax.set_ylim(ylim)
        self.ax.set_xlim(self.data_viz_control.xlim)
        self.spectogram_window.draw()

    def on_lower_bound_change(self, value):
        # Function to handle lower bound value changes
        self.data_viz_upper_bound_slider.config(
            to=self.data_viz_lower_bound_slider.get())

        self.draw_spectogram()

    def on_upper_bound_change(self, value):
        # Function to handle upper bound value changes
        self.data_viz_lower_bound_slider.config(
            from_=self.data_viz_upper_bound_slider.get())

        self.draw_spectogram()

    def on_vmin_change(self, value):
        # Function to handle vmin value changes
        self.data_viz_vmax_slider.config(from_=self.data_viz_vmin_slider.get())
        self.draw_spectogram()

    def on_vmax_change(self, value):
        # Function to handle vmax value changes
        self.data_viz_vmin_slider.config(to=self.data_viz_vmax_slider.get())
        self.draw_spectogram()


UPDATE_INTERVAL = round(1/24 * 1000)


def update_clip_signal(signal_clipper):

    # signal_clipper.draw_spectogram()
    signal_clipper.root.after(UPDATE_INTERVAL, partial(
        update_clip_signal, signal_clipper))


def clip_signal(data, sampling_rate):

    root = tk.Tk()

    signal_clipper = SignalClipper(root, data, sampling_rate)

    signal_clipper.draw_spectogram()

    root.after(UPDATE_INTERVAL, partial(update_clip_signal, signal_clipper))
    root.mainloop()

    return signal_clipper.data_viz_control.xlim
