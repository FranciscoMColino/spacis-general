import tkinter as tk
from tkinter import *
from tkinter.ttk import *


def open_position_def(root, delay_control):
    top= Toplevel(root)

    main_frame = tk.Frame(top, bd=1, relief=tk.FLAT)
    main_frame.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(main_frame, text="Subwoofer Array Position Definition", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)