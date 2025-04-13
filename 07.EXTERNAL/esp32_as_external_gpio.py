import time
from machine import Pin, ADC, DAC, I2C, SPI, Timer
import machine
machine.freq(240000000)

# Constants for I2C pins
I2C_SDA_PIN = 21  # GPIO21
I2C_SCL_PIN = 22  # GPIO22

# Initialize I2C with explicit initialization
def init_i2c(scl_pin, sda_pin, freq=400000):
    return I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=freq)

i2c = init_i2c(I2C_SCL_PIN, I2C_SDA_PIN)

# GPIO table excluding I2C pins
GPIO_PINS = {
    0: {"Function": "Digital I/O"},
    1: {"Function": "Digital I/O, UART TX0"},
    2: {"Function": "Digital I/O"},
    3: {"Function": "Digital I/O, UART RX0"},
    4: {"Function": "Digital I/O, PWM, ADC"},
    5: {"Function": "Digital I/O, PWM, ADC, HSPI_SS"},
    12: {"Function": "Digital I/O, ADC2, DAC2"},
    13: {"Function": "Digital I/O, PWM, ADC2, Touch4"},
    14: {"Function": "Digital I/O, PWM, ADC2, HSPI_CLK"},
    15: {"Function": "Digital I/O, PWM, ADC2, HSPI_CS"},
    16: {"Function": "Digital I/O, PWM, U2_RXD"},
    17: {"Function": "Digital I/O, PWM, U2_TXD"},
    18: {"Function": "Digital I/O, PWM, VSPI_CLK"},
    19: {"Function": "Digital I/O, PWM, VSPI_MISO"},
    21: {"Function": "Digital I/O, I2C SDA"},
    22: {"Function": "Digital I/O, I2C SCL"},
    23: {"Function": "Digital I/O, PWM, VSPI_MOSI"},
    25: {"Function": "Digital I/O, ADC2, DAC1"},
    26: {"Function": "Digital I/O, ADC2, DAC1"},
    27: {"Function": "Digital I/O, ADC2, Touch7"},
    32: {"Function": "Digital I/O, ADC1, Touch9"},
    33: {"Function": "Digital I/O, ADC1, Touch8"},
    34: {"Function": "Digital I/O, ADC1, Input only"},
    35: {"Function": "Digital I/O, ADC1, Input only"},
    36: {"Function": "Digital I/O, ADC1, Input only"},
    39: {"Function": "Digital I/O, ADC1, Input only"},
}


# GPIO Control Class
class GPIOControl:
    @staticmethod
    def digital_write(pin, value):
        if pin in GPIO_PINS:
            p = Pin(pin, Pin.OUT)
            p.value(value)
            print(f"GPIO{pin}: {value}")
        else:
            print(f"Invalid GPIO pin: {pin}")

    @staticmethod
    def digital_read(pin):
        if pin in GPIO_PINS:
            p = Pin(pin, Pin.IN)
            value = p.value()
            print(f"GPIO{pin}: {value}")
            return value
        else:
            print(f"Invalid GPIO pin: {pin}")

    @staticmethod
    def analog_read(pin):
        if pin in GPIO_PINS:
            adc = ADC(Pin(pin))
            value = adc.read()
            print(f"GPIO{pin}: {value}")
            return value
        else:
            print(f"Invalid GPIO pin: {pin}")

    @staticmethod
    def analog_write(pin, value):
        if pin in GPIO_PINS:
            if 0 <= value <= 255:
                dac = DAC(Pin(pin))
                dac.write(value)
                print(f"GPIO{pin}: {value}")
            else:
                print("Analog write value must be between 0 and 255.")
        else:
            print(f"Invalid GPIO pin: {pin}")


# I2C Control Class
class I2CControl:
    @staticmethod
    def i2c_scan(delay_ms=500):
        print("Scanning I2C bus...")
        time.sleep_ms(delay_ms)
        devices = i2c.scan()
        if devices:
            print(f"Detected I2C devices: {devices}")
        else:
            print("No I2C devices found.")
        return devices

    @staticmethod
    def i2c_read(addr, nbytes, timeout=1000, retries=3):
        attempt = 0
        while attempt < retries:
            try:
                data = i2c.readfrom(addr, nbytes)
                print(f"Read from I2C address {addr}: {data}")
                return data
            except Exception as e:
                print(f"I2C read error: {e}, attempt {attempt + 1}/{retries}")
                time.sleep_ms(timeout)
                attempt += 1
        print("I2C read failed after multiple attempts.")
        return None

    @staticmethod
    def i2c_write(addr, data, timeout=1000, retries=3):
        attempt = 0
        while attempt < retries:
            try:
                i2c.writeto(addr, data)
                print(f"Written to I2C address {addr}: {data}")
                return
            except Exception as e:
                print(f"I2C write error: {e}, attempt {attempt + 1}/{retries}")
                time.sleep_ms(timeout)
                attempt += 1
        print("I2C write failed after multiple attempts.")


# SPI Control Class
class SPIControl:
    @staticmethod
    def spi_transfer(mosi_pin, miso_pin, sck_pin, data, timeout=1000, retries=3):
        attempt = 0
        while attempt < retries:
            try:
                spi = SPI(1, baudrate=1000000, polarity=0, phase=0, mosi=Pin(mosi_pin), miso=Pin(miso_pin), sck=Pin(sck_pin))
                result = spi.write_readinto(data, data)
                print(f"SPI transfer result: {data}")
                return data
            except Exception as e:
                print(f"SPI transfer error: {e}, attempt {attempt + 1}/{retries}")
                time.sleep_ms(timeout)
                attempt += 1
        print("SPI transfer failed after multiple attempts.")
        return None


class CommandParser:
    def __init__(self):
        self.commands = {
            'digital_write': GPIOControl.digital_write,
            'digital_read': GPIOControl.digital_read,
            'analog_read': GPIOControl.analog_read,
            'analog_write': GPIOControl.analog_write,
            'i2c_scan': I2CControl.i2c_scan,
            'i2c_read': I2CControl.i2c_read,
            'i2c_write': I2CControl.i2c_write,
            'spi_transfer': SPIControl.spi_transfer,
            'help': self.print_help,
            'gpio_table': self.print_gpio_table,
        }

    def execute_command(self, command):
        try:
            # Check if command is a function call or standalone function
            if '(' in command and ')' in command:
                command_name, args = command.split('(', 1)
                args = args.rstrip(')')
                
                if args:
                    # Convert the argument string into a tuple
                    if ',' in args:
                        args = eval(f"({args})")
                    else:
                        args = (eval(args),)  # Single argument case
                else:
                    args = ()  # No arguments
                
                # Call the appropriate function with the provided arguments
                if command_name in self.commands:
                    self.commands[command_name](*args)
                else:
                    print(f"Unknown command: {command_name}")
            else:
                # Handle standalone function calls like 'i2c_scan'
                if command in self.commands:
                    self.commands[command]()
                else:
                    print(f"Unknown command: {command}")
        except Exception as e:
            print(f"Error: {e}")

    def print_help(self):
        print("""
        Available Commands:
        - digital_write(pin, value): Write digital value (0/1) to a GPIO pin.
        - digital_read(pin): Read digital value (0/1) from a GPIO pin.
        - analog_read(pin): Read analog value (0-4095) from an ADC pin.
        - analog_write(pin, value): Write analog value (0-255) to a DAC pin.
        - i2c_scan(): Scan I2C bus and return detected addresses.
        - i2c_read(addr, nbytes): Read nbytes from I2C device at addr.
        - i2c_write(addr, data): Write data to I2C device at addr.
        - spi_transfer(mosi_pin, miso_pin, sck_pin, data): Transfer data via SPI.
        - gpio_table(): Print the GPIO table.
        - help(): Show this help message.
        """)

    def print_gpio_table(self):
        print("GPIO Table:")
        for pin, details in GPIO_PINS.items():
            print(f"GPIO{pin}: Function: {details['Function']}")


# Event Handling with Power Management and Extensibility
class EventHandler:
    def __init__(self):
        self.commands = CommandParser()
        self.timer = Timer(0)

    def handle_events(self):
        print("ESP32 GPIO Control Ready.")
        self.commands.print_gpio_table()
        self.commands.print_help()

        while True:
            try:
                command = input(">>> ")
                if command.strip().lower() == "exit":
                    print("Exiting...")
                    break
                self.commands.execute_command(command)
            except Exception as e:
                print(f"Error: {e}")

    def sleep_mode(self, mode):
        if mode == "light":
            print("Entering light sleep mode...")
            machine.lightsleep()  # Enter light sleep mode
        elif mode == "deep":
            print("Entering deep sleep mode...")
            machine.deepsleep()  # Enter deep sleep mode
        else:
            print("Invalid sleep mode specified.")

    def schedule_event(self, callback, delay_ms):
        print(f"Scheduling event in {delay_ms}ms.")
        self.timer.init(period=delay_ms, mode=Timer.ONE_SHOT, callback=lambda t: callback())


# Initialize and run the event handler
event_handler = EventHandler()
event_handler.handle_events()
