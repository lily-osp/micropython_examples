import tkinter as tk
from tkinter import messagebox
from 07.EXTERNAL.esp32_as_external_gpio import GPIOControl, I2CControl, SPIControl, CommandParser, EventHandler

class ESP32GPIOUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 GPIO Control")

        self.create_widgets()

    def create_widgets(self):
        # Digital Write
        self.digital_write_frame = tk.Frame(self.root)
        self.digital_write_frame.pack(pady=10)

        self.digital_write_label = tk.Label(self.digital_write_frame, text="Digital Write")
        self.digital_write_label.grid(row=0, column=0, columnspan=2)

        self.digital_write_pin_label = tk.Label(self.digital_write_frame, text="Pin:")
        self.digital_write_pin_label.grid(row=1, column=0)
        self.digital_write_pin_entry = tk.Entry(self.digital_write_frame)
        self.digital_write_pin_entry.grid(row=1, column=1)

        self.digital_write_value_label = tk.Label(self.digital_write_frame, text="Value (0/1):")
        self.digital_write_value_label.grid(row=2, column=0)
        self.digital_write_value_entry = tk.Entry(self.digital_write_frame)
        self.digital_write_value_entry.grid(row=2, column=1)

        self.digital_write_button = tk.Button(self.digital_write_frame, text="Write", command=self.digital_write)
        self.digital_write_button.grid(row=3, column=0, columnspan=2)

        # Digital Read
        self.digital_read_frame = tk.Frame(self.root)
        self.digital_read_frame.pack(pady=10)

        self.digital_read_label = tk.Label(self.digital_read_frame, text="Digital Read")
        self.digital_read_label.grid(row=0, column=0, columnspan=2)

        self.digital_read_pin_label = tk.Label(self.digital_read_frame, text="Pin:")
        self.digital_read_pin_label.grid(row=1, column=0)
        self.digital_read_pin_entry = tk.Entry(self.digital_read_frame)
        self.digital_read_pin_entry.grid(row=1, column=1)

        self.digital_read_button = tk.Button(self.digital_read_frame, text="Read", command=self.digital_read)
        self.digital_read_button.grid(row=2, column=0, columnspan=2)

        self.digital_read_result_label = tk.Label(self.digital_read_frame, text="Result:")
        self.digital_read_result_label.grid(row=3, column=0)
        self.digital_read_result_value = tk.Label(self.digital_read_frame, text="")
        self.digital_read_result_value.grid(row=3, column=1)

        # Analog Read
        self.analog_read_frame = tk.Frame(self.root)
        self.analog_read_frame.pack(pady=10)

        self.analog_read_label = tk.Label(self.analog_read_frame, text="Analog Read")
        self.analog_read_label.grid(row=0, column=0, columnspan=2)

        self.analog_read_pin_label = tk.Label(self.analog_read_frame, text="Pin:")
        self.analog_read_pin_label.grid(row=1, column=0)
        self.analog_read_pin_entry = tk.Entry(self.analog_read_frame)
        self.analog_read_pin_entry.grid(row=1, column=1)

        self.analog_read_button = tk.Button(self.analog_read_frame, text="Read", command=self.analog_read)
        self.analog_read_button.grid(row=2, column=0, columnspan=2)

        self.analog_read_result_label = tk.Label(self.analog_read_frame, text="Result:")
        self.analog_read_result_label.grid(row=3, column=0)
        self.analog_read_result_value = tk.Label(self.analog_read_frame, text="")
        self.analog_read_result_value.grid(row=3, column=1)

        # Analog Write
        self.analog_write_frame = tk.Frame(self.root)
        self.analog_write_frame.pack(pady=10)

        self.analog_write_label = tk.Label(self.analog_write_frame, text="Analog Write")
        self.analog_write_label.grid(row=0, column=0, columnspan=2)

        self.analog_write_pin_label = tk.Label(self.analog_write_frame, text="Pin:")
        self.analog_write_pin_label.grid(row=1, column=0)
        self.analog_write_pin_entry = tk.Entry(self.analog_write_frame)
        self.analog_write_pin_entry.grid(row=1, column=1)

        self.analog_write_value_label = tk.Label(self.analog_write_frame, text="Value (0-255):")
        self.analog_write_value_label.grid(row=2, column=0)
        self.analog_write_value_entry = tk.Entry(self.analog_write_frame)
        self.analog_write_value_entry.grid(row=2, column=1)

        self.analog_write_button = tk.Button(self.analog_write_frame, text="Write", command=self.analog_write)
        self.analog_write_button.grid(row=3, column=0, columnspan=2)

    def digital_write(self):
        try:
            pin = int(self.digital_write_pin_entry.get())
            value = int(self.digital_write_value_entry.get())
            GPIOControl.digital_write(pin, value)
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid pin and value.")

    def digital_read(self):
        try:
            pin = int(self.digital_read_pin_entry.get())
            value = GPIOControl.digital_read(pin)
            self.digital_read_result_value.config(text=str(value))
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a valid pin.")

    def analog_read(self):
        try:
            pin = int(self.analog_read_pin_entry.get())
            value = GPIOControl.analog_read(pin)
            self.analog_read_result_value.config(text=str(value))
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a valid pin.")

    def analog_write(self):
        try:
            pin = int(self.analog_write_pin_entry.get())
            value = int(self.analog_write_value_entry.get())
            GPIOControl.analog_write(pin, value)
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid pin and value.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ESP32GPIOUI(root)
    root.mainloop()
