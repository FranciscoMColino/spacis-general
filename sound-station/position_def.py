import tkinter as tk
from tkinter import *
from tkinter.ttk import *


def open_position_def(root, delay_control):
    top= Toplevel(root)

    main_frame = tk.Frame(top, bd=1, relief=tk.FLAT)
    main_frame.grid(row=0, column=0, padx=10, pady=10)

    tk.Label(main_frame, text="Subwoofer Array Position Definition").grid(row=0, column=0, pady=10)

    pos_frame = tk.Frame(main_frame, bd=1, relief=tk.FLAT)
    pos_frame.grid(row=1, column=0, padx=10, pady=10)
    
    for i in range(6):

        sub_pos_frame = tk.Frame(pos_frame, bd=1, relief=tk.FLAT)
        sub_pos_frame.grid(row=i//2, column=i%2, padx=10, pady=10)

        tk.Label(sub_pos_frame, text="Subwoofer {}".format(i)).grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        tk.Label(sub_pos_frame, text="Orientation").grid(row=1, column=0, padx=10, pady=10)

        entry = tk.Entry(sub_pos_frame, textvariable=delay_control.subwoofer_array["sub{}".format(i)]["raw_pos_data"]["orientation_tk"])
        entry.grid(row=1, column=1, padx=10, pady=10)
