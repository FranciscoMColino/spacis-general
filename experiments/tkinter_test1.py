import tkinter as tk
from tkinter import messagebox


def show_result():
    result = "Button was clicked!"
    messagebox.showinfo("Result", result)
    root.quit()  # Close the tkinter window and return a result


root = tk.Tk()
root.title("Tkinter App")

label = tk.Label(root, text="Click the button to get a result:")
label.pack(pady=10)

button = tk.Button(root, text="Click Me", command=show_result)
button.pack()

root.mainloop()

# This part of the code will be executed when the tkinter window is closed
result = "Window was closed!"
print(result)
