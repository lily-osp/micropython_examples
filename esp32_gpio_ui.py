import tkinter as tk
from tkinter import scrolledtext
import serial
import threading
import queue
import time

class ESP32GPIOUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 GPIO Control")

        self.serial_port = None
        self.is_running = True
        self.serial_queue = queue.Queue()

        self.create_widgets()
        self.connect_to_esp32()

        # Start the serial reading thread
        self.serial_thread = threading.Thread(target=self.read_from_serial, daemon=True)
        self.serial_thread.start()

        # Start updating the GUI
        self.update_gui()

        # Bind the closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def connect_to_esp32(self):
        try:
            self.serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=0)
            self.log_to_terminal("Connected to ESP32")
        except serial.SerialException as e:
            self.log_to_terminal(f"Failed to connect to ESP32: {e}")
            self.serial_port = None

    def create_widgets(self):
        # Terminal Window
        self.terminal_frame = tk.Frame(self.root)
        self.terminal_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.terminal_label = tk.Label(self.terminal_frame, text="Terminal")
        self.terminal_label.pack()

        self.terminal_text = scrolledtext.ScrolledText(self.terminal_frame, wrap=tk.WORD, width=60, height=20)
        self.terminal_text.pack(fill=tk.BOTH, expand=True)

        # Command Entry
        self.command_frame = tk.Frame(self.root)
        self.command_frame.pack(pady=10, padx=10)

        self.command_entry = tk.Entry(self.command_frame, width=50)
        self.command_entry.pack(side=tk.LEFT, padx=10)

        self.send_command_button = tk.Button(self.command_frame, text="Send Command", command=self.send_custom_command)
        self.send_command_button.pack(side=tk.LEFT)

        # Control Frame
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10, padx=10)

        # GPIO Control
        self.gpio_frame = tk.Frame(self.control_frame)
        self.gpio_frame.pack(side=tk.LEFT, padx=10)

        self.gpio_label = tk.Label(self.gpio_frame, text="GPIO Control")
        self.gpio_label.grid(row=0, column=0, columnspan=2)

        self.gpio_pin_label = tk.Label(self.gpio_frame, text="Pin:")
        self.gpio_pin_label.grid(row=1, column=0)
        self.gpio_pin_entry = tk.Entry(self.gpio_frame, width=5)
        self.gpio_pin_entry.grid(row=1, column=1)

        self.gpio_value_label = tk.Label(self.gpio_frame, text="Value:")
        self.gpio_value_label.grid(row=2, column=0)
        self.gpio_value_entry = tk.Entry(self.gpio_frame, width=5)
        self.gpio_value_entry.grid(row=2, column=1)

        self.digital_read_button = tk.Button(self.gpio_frame, text="Digital Read", command=self.digital_read)
        self.digital_read_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.digital_write_button = tk.Button(self.gpio_frame, text="Digital Write", command=self.digital_write)
        self.digital_write_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.analog_read_button = tk.Button(self.gpio_frame, text="Analog Read", command=self.analog_read)
        self.analog_read_button.grid(row=5, column=0, columnspan=2, pady=5)

        self.analog_write_button = tk.Button(self.gpio_frame, text="Analog Write", command=self.analog_write)
        self.analog_write_button.grid(row=6, column=0, columnspan=2, pady=5)

    def send_custom_command(self):
        command = self.command_entry.get().strip()
        if command:
            self.send_command(command)
            self.command_entry.delete(0, tk.END)


    def log_to_terminal(self, message):
        self.serial_queue.put(message)

    def update_gui(self):
        while not self.serial_queue.empty():
            message = self.serial_queue.get()
            self.terminal_text.insert(tk.END, f"{message}\n")
            self.terminal_text.see(tk.END)
        self.root.after(100, self.update_gui)

    def read_from_serial(self):
        buffer = ""
        while self.is_running:
            if self.serial_port and self.serial_port.is_open:
                try:
                    # Read data from the serial port
                    data = self.serial_port.read(self.serial_port.in_waiting or 1).decode('utf-8', errors='replace')

                    # Append to the buffer
                    buffer += data

                    # Check if the response is complete (ends with ">>> ")
                    if ">>> " in buffer:
                        # Process the full response
                        self.serial_queue.put(buffer.strip())

                        # Clear the buffer for the next command
                        buffer = ""

                except serial.SerialException:
                    self.log_to_terminal("Serial connection lost. Attempting to reconnect...")
                    self.connect_to_esp32()

            time.sleep(0.1)


    def send_command(self, command):
        if not self.serial_port or not self.serial_port.is_open:
            self.log_to_terminal("Not connected to ESP32. Please check the connection.")
            return
        try:
            self.log_to_terminal(f"Sending: {command}")
            self.serial_port.write((command + '\n').encode())
            time.sleep(0.1)
        except serial.SerialException as e:
            self.log_to_terminal(f"Failed to send command: {e}")

    def digital_read(self):
        try:
            pin = int(self.gpio_pin_entry.get())
            self.send_command(f'digital_read({pin})')
        except ValueError:
            self.log_to_terminal("Invalid input. Please enter a valid pin number.")

    def digital_write(self):
        try:
            pin = int(self.gpio_pin_entry.get())
            value = int(self.gpio_value_entry.get())
            if value not in [0, 1]:
                raise ValueError
            self.send_command(f'digital_write({pin}, {value})')
        except ValueError:
            self.log_to_terminal("Invalid input. Please enter a valid pin number and value (0 or 1).")

    def analog_read(self):
        try:
            pin = int(self.gpio_pin_entry.get())
            self.send_command(f'analog_read({pin})')
        except ValueError:
            self.log_to_terminal("Invalid input. Please enter a valid pin number.")

    def analog_write(self):
        try:
            pin = int(self.gpio_pin_entry.get())
            value = int(self.gpio_value_entry.get())
            if not 0 <= value <= 255:
                raise ValueError
            self.send_command(f'analog_write({pin}, {value})')
        except ValueError:
            self.log_to_terminal("Invalid input. Please enter a valid pin number and value (0-255).")

    def on_closing(self):
        self.is_running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ESP32GPIOUI(root)
    root.mainloop()
