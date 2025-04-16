from machine import SoftI2C, Pin
from i2c_lcd import I2cLcd
import time
import urandom

# Configuration
I2C_SCL_PIN = 5
I2C_SDA_PIN = 4
I2C_FREQ = 400000
I2C_ADDR = 0x27  # Common addresses: 0x27 or 0x3F

# Initialize I2C and LCD
i2c = SoftI2C(scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)
lcd = I2cLcd(i2c, I2C_ADDR, num_lines=2, num_columns=16)

# Custom characters (8x5 pixel bitmaps)
CUSTOM_CHARS = [
    bytearray([0x00, 0x0A, 0x1F, 0x1F, 0x1F, 0x0E, 0x04, 0x00]),  # Heart (0)
    bytearray([0x04, 0x0E, 0x0E, 0x0E, 0x1F, 0x00, 0x04, 0x00]),  # Arrow (1)
    bytearray([0x1F, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1F, 0x00]),  # Box (2)
    bytearray([0x0E, 0x0E, 0x0E, 0x1F, 0x04, 0x04, 0x04, 0x00]),  # Checkmark (3)
    bytearray([0x0A, 0x1F, 0x1F, 0x00, 0x04, 0x0A, 0x11, 0x00]),  # Smiley (4)
    bytearray([0x00, 0x04, 0x0E, 0x1F, 0x0E, 0x04, 0x00, 0x00]),  # Star (5)
    bytearray([0x04, 0x0E, 0x0E, 0x1F, 0x1F, 0x04, 0x0A, 0x00]),  # Bell (6)
    bytearray([0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F]),  # Solid block (7)
]


def load_custom_chars():
    """Load all custom characters into CGRAM."""
    for i, char in enumerate(CUSTOM_CHARS):
        lcd.create_char(i, char)


class LCDDemo:
    @staticmethod
    def welcome_screen():
        """Display welcome screen with version info."""
        lcd.clear()
        lcd.print_at(0, 0, "LCD Demo v2.0")
        lcd.print_at(0, 1, "Press Ctrl+C exit")
        time.sleep(2)

    @staticmethod
    def hardware_test():
        """Basic LCD hardware test."""
        # Test display on/off
        lcd.clear()
        lcd.print_at(0, 0, "Display Test")
        time.sleep(1)

        lcd.set_display(False)
        time.sleep(1)
        lcd.set_display(True)
        time.sleep(1)

        # Test backlight
        lcd.print_at(0, 1, "Backlight Test")
        time.sleep(1)

        for _ in range(3):
            lcd.set_backlight(False)
            time.sleep(0.5)
            lcd.set_backlight(True)
            time.sleep(0.5)

        # Test cursor modes
        lcd.clear()
        lcd.print_at(0, 0, "Cursor Test")

        # Normal cursor
        lcd.set_cursor(True)
        lcd.set_blink(False)
        lcd.print_at(0, 1, "Normal cursor")
        time.sleep(2)

        # Blinking cursor
        lcd.set_cursor(True)
        lcd.set_blink(True)
        lcd.print_at(0, 1, "Blinking cursor")
        time.sleep(2)

        # Turn off cursor
        lcd.set_cursor(False)
        lcd.set_blink(False)

    @staticmethod
    def rotation_demo():
        """Demonstrate different rotation modes."""
        lcd.clear()
        lcd.print_at(0, 0, "Rotation Demo")
        time.sleep(1)

        rotations = [
            (lcd.ROTATION_NORMAL, "Normal (0)"),
            (lcd.ROTATION_90, "90 degrees"),
            (lcd.ROTATION_180, "180 degrees"),
            (lcd.ROTATION_270, "270 degrees"),
        ]

        for rotation, desc in rotations:
            lcd.clear()
            lcd.set_rotation(rotation)
            # Display coordinates for reference
            for y in range(lcd.num_lines):
                for x in range(min(lcd.num_columns, 16)):
                    if x % 5 == 0 and y % 2 == 0:
                        lcd.move_to(x, y)
                        lcd.putchar(chr(x // 5 + ord("0")))

            # Show rotation info
            lcd.set_rotation(lcd.ROTATION_NORMAL)  # Reset to show text normally
            lcd.print_at(0, 1, desc)
            time.sleep(2)

        # Reset to normal rotation
        lcd.set_rotation(lcd.ROTATION_NORMAL)

    @staticmethod
    def text_direction_demo():
        """Demonstrate left-to-right and right-to-left text."""
        lcd.clear()
        lcd.print_at(0, 0, "Text Direction")
        time.sleep(1)

        # Left to right (default)
        lcd.clear()
        lcd.set_text_direction(True)
        lcd.print_at(0, 0, "Left to Right")
        lcd.move_to(0, 1)
        for c in "12345":
            lcd.putchar(c)
            time.sleep(0.5)
        time.sleep(1)

        # Right to left
        lcd.clear()
        lcd.set_text_direction(False)
        lcd.print_at(0, 0, "Right to Left")
        lcd.move_to(15, 1)  # Start from right edge
        for c in "12345":
            lcd.putchar(c)
            time.sleep(0.5)
        time.sleep(1)

        # Reset to left-to-right
        lcd.set_text_direction(True)

    @staticmethod
    def scroll_demo():
        """Demonstrate various scrolling features."""
        lcd.clear()
        lcd.print_at(0, 0, "Scroll Demo")
        time.sleep(1)

        # Using the scroll method
        lcd.clear()
        lcd.print_at(0, 0, "Display scroll")
        lcd.print_at(0, 1, "Left <-> Right")
        time.sleep(1)

        # Scroll right
        for _ in range(5):
            lcd.scroll(1)  # Right
            time.sleep(0.3)

        # Scroll left
        for _ in range(10):
            lcd.scroll(-1)  # Left
            time.sleep(0.3)

        # Scroll right to center again
        for _ in range(5):
            lcd.scroll(1)
            time.sleep(0.3)

        # Text scrolling
        lcd.clear()
        lcd.print_at(0, 0, "Text scroll:")
        time.sleep(1)

        # Use the built-in scroll_text method
        lcd.scroll_text(
            1,
            "This is a long scrolling message that demonstrates the new scrolling feature",
            delay=200,
            repeat=1,
        )

    @staticmethod
    def progress_bar_demo():
        """Demonstrate progress bar functionality."""
        lcd.clear()
        lcd.print_at(0, 0, "Progress Bar")

        # Show progress from 0 to 100%
        for i in range(21):
            progress = i / 20.0
            lcd.create_progress_bar(1, progress)
            lcd.move_to(0, 0)
            lcd.putstr(f"Progress: {int(progress*100):3d}%")
            time.sleep(0.2)

        time.sleep(1)

    @staticmethod
    def animation_demo():
        """Demonstrate animation capabilities."""
        lcd.clear()
        lcd.print_at(0, 0, "Animation Demo")
        time.sleep(1)

        # Simple animation frames
        frames = [
            "Loading    ",
            "Loading .  ",
            "Loading .. ",
            "Loading ...",
        ]

        # Use the built-in animation method
        lcd.create_animation(1, frames, delay=300, repeat=2)

        # Bounce effect with custom char
        lcd.clear()
        lcd.print_at(0, 0, "Bounce effect")

        char_pos = 0
        direction = 1

        for _ in range(30):
            # Clear previous position
            lcd.move_to(0, 1)
            lcd.putstr(" " * 16)

            # Draw at new position
            lcd.move_to(char_pos, 1)
            lcd.putchar(chr(5))  # Star character

            # Update position
            char_pos += direction
            if char_pos >= 15 or char_pos <= 0:
                direction = -direction

            time.sleep(0.1)

    @staticmethod
    def custom_char_showcase():
        """Show all custom characters with labels."""
        names = ["Heart", "Arrow", "Box", "Check", "Smile", "Star", "Bell", "Block"]
        lcd.clear()
        lcd.print_at(0, 0, "Custom Chars:")

        for i, name in enumerate(names):
            lcd.clear()
            lcd.print_at(0, 0, f"Char {i}: {name}")
            lcd.move_to(8, 1)
            lcd.putchar(chr(i))
            time.sleep(1)

    @staticmethod
    def buffer_demo():
        """Demonstrate buffer-based operations."""
        lcd.clear()
        lcd.print_at(0, 0, "Buffer Demo")
        time.sleep(1)

        # Fill the buffer with pattern
        for y in range(lcd.num_lines):
            for x in range(lcd.num_columns):
                lcd.buffer[y][x] = chr((x + y) % 8)  # Use custom chars

        # Refresh to display buffer contents
        lcd.refresh()
        time.sleep(2)

        # Modify buffer and refresh again
        for y in range(lcd.num_lines):
            for x in range(lcd.num_columns):
                if (x + y) % 2 == 0:
                    lcd.buffer[y][x] = " "

        lcd.refresh()
        time.sleep(2)

    @staticmethod
    def run_demo_sequence():
        """Run all demos in sequence."""
        demos = [
            LCDDemo.welcome_screen,
            LCDDemo.hardware_test,
            LCDDemo.rotation_demo,
            LCDDemo.text_direction_demo,
            LCDDemo.scroll_demo,
            LCDDemo.progress_bar_demo,
            LCDDemo.animation_demo,
            LCDDemo.custom_char_showcase,
            LCDDemo.buffer_demo,
        ]

        try:
            while True:
                for demo in demos:
                    demo()
                    time.sleep(1)

                # Final message before looping
                lcd.clear()
                lcd.print_at(0, 0, "Demo completed")
                lcd.print_at(0, 1, "Restarting...")
                time.sleep(2)

        except KeyboardInterrupt:
            pass


def gpio_test():
    """Test if GPIO pins are working properly."""
    try:
        # Blink backlight as a simple test
        lcd.clear()
        lcd.print_at(0, 0, "GPIO Test")
        lcd.print_at(0, 1, "Backlight blink")

        for _ in range(3):
            lcd.set_backlight(False)
            time.sleep(0.5)
            lcd.set_backlight(True)
            time.sleep(0.5)

        return True
    except Exception as e:
        print("GPIO Test failed:", e)
        return False


def i2c_scan():
    """Scan I2C bus for devices and return addresses."""
    try:
        devices = i2c.scan()
        return devices
    except Exception as e:
        print("I2C scan failed:", e)
        return []


def diagnostic_mode():
    """Run diagnostic tests on the LCD and I2C bus."""
    lcd.clear()
    lcd.print_at(0, 0, "Diagnostics")
    time.sleep(1)

    # I2C scan
    lcd.clear()
    lcd.print_at(0, 0, "I2C scan...")
    devices = i2c_scan()

    if devices:
        lcd.print_at(0, 1, f"Found: {' '.join([hex(d) for d in devices])}")
    else:
        lcd.print_at(0, 1, "No devices found")

    time.sleep(2)

    # GPIO test
    lcd.clear()
    lcd.print_at(0, 0, "Testing GPIO...")
    gpio_ok = gpio_test()

    lcd.clear()
    lcd.print_at(0, 0, "GPIO Test:")
    lcd.print_at(0, 1, "OK" if gpio_ok else "FAILED")

    time.sleep(2)

    # Display test pattern
    lcd.clear()
    lcd.print_at(0, 0, "Display pattern")

    # Fill with alternating blocks
    for y in range(lcd.num_lines):
        for x in range(lcd.num_columns):
            lcd.move_to(x, y)
            lcd.putchar(chr(7 if (x + y) % 2 == 0 else 2))

    time.sleep(2)

    # All pixels on test
    lcd.clear()
    lcd.print_at(0, 0, "All pixels test")
    time.sleep(1)

    # Fill entire display with solid blocks
    for y in range(lcd.num_lines):
        for x in range(lcd.num_columns):
            lcd.move_to(x, y)
            lcd.putchar(chr(7))  # Solid block character

    time.sleep(2)


if __name__ == "__main__":
    try:
        lcd.set_backlight(True)
        load_custom_chars()

        # Check for diagnostic mode (could be triggered by a button in real setup)
        run_diagnostics = False

        if run_diagnostics:
            diagnostic_mode()
        else:
            # Run the demo sequence
            LCDDemo.run_demo_sequence()

    except KeyboardInterrupt:
        # Clean exit with Ctrl+C
        lcd.clear()
        lcd.set_backlight(False)
    except Exception as e:
        # Show error on display
        lcd.clear()
        lcd.print_at(0, 0, "Error:")
        # Truncate error message to fit on display
        error_msg = str(e)
        if len(error_msg) > 16:
            error_msg = error_msg[:13] + "..."
        lcd.print_at(0, 1, error_msg)

        # Wait a bit before turning off
        time.sleep(5)
        lcd.clear()
        lcd.set_backlight(False)

        # Re-raise for debugging
        raise
