from machine import I2C
import time


class I2cLcd:
    """
    Driver for I2C LCD displays with PCF8574 I2C backpack.
    Supports various display sizes.
    """
    # LCD command constants
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # Entry mode flags
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # Display control flags
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # Function set flags
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    # Backlight control
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00

    # Control bits
    ENABLE = 0x04
    RS_DATA = 0x01
    RS_COMMAND = 0x00

    def __init__(self, i2c, i2c_addr, num_lines, num_columns, line_offsets, char_size=LCD_5x8DOTS):
        """
        Initialize the LCD with provided parameters.

        Args:
            i2c: I2C bus object
            i2c_addr: I2C address of the LCD (typically 0x27 or 0x3F)
            num_lines: Number of display lines (e.g., 2 for 1602, 4 for 2004)
            num_columns: Number of characters per line (e.g., 16 for 1602, 20 for 2004)
            line_offsets: List of DDRAM address offsets for each line
            char_size: Character size (LCD_5x8DOTS or LCD_5x10DOTS)
        """
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self._line_offsets = line_offsets
        self.cursor_x = 0
        self.cursor_y = 0
        self.backlight = self.LCD_BACKLIGHT
        self.display_control = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.display_function = self.LCD_4BITMODE | (self.LCD_2LINE if num_lines > 1 else self.LCD_1LINE)
        self.display_function |= char_size
        self.display_mode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        
        # Buffer for storing display content
        self.buffer = [[" " for x in range(num_columns)] for y in range(num_lines)]
        
        # Debugging: Print configuration
        print(f"LCD Config: {num_columns}x{num_lines}, Address: {hex(i2c_addr)}, Offsets: {[hex(o) for o in line_offsets]}")

    def init_display(self):
        """Initialize the display in 4-bit mode."""
        # Extended wait for power-on to handle 20x4 displays
        time.sleep_ms(100)

        # Initialization sequence for 4-bit mode
        self._write_nibble(0x30)
        time.sleep_ms(5)
        self._write_nibble(0x30)
        time.sleep_us(100)
        self._write_nibble(0x30)
        time.sleep_us(100)
        self._write_nibble(0x20)  # Set 4-bit mode
        time.sleep_us(100)

        # Configure display
        self._write_command(self.LCD_FUNCTIONSET | self.display_function)
        self._write_command(self.LCD_DISPLAYCONTROL | self.display_control)
        self.clear()
        self._write_command(self.LCD_ENTRYMODESET | self.display_mode)

        # Turn on display with configured settings
        self.set_display(True)
        print("LCD Initialized")

    def _write_nibble(self, nibble):
        """Write a nibble (4 bits) to the LCD."""
        data = nibble | self.backlight
        self.i2c.writeto(self.i2c_addr, bytearray([data | self.ENABLE]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytearray([data & ~self.ENABLE]))
        time.sleep_us(50)

    def _write_byte(self, byte, rs_mode):
        """Write a byte to the LCD."""
        high_nibble = byte & 0xF0
        low_nibble = (byte << 4) & 0xF0
        self._write_nibble(high_nibble | rs_mode)
        self._write_nibble(low_nibble | rs_mode)

    def _write_command(self, command):
        """Write a command to the LCD."""
        self._write_byte(command, self.RS_COMMAND)

    def _write_data(self, data):
        """Write data to the LCD."""
        self._write_byte(data, self.RS_DATA)

    def clear(self):
        """Clear the display and return cursor to home position."""
        self._write_command(self.LCD_CLEARDISPLAY)
        time.sleep_ms(3)  # Clear command needs extra time
        self.cursor_x = 0
        self.cursor_y = 0
        # Clear buffer
        for y in range(self.num_lines):
            for x in range(self.num_columns):
                self.buffer[y][x] = " "
        print("Display Cleared")

    def home(self):
        """Return cursor to home position (0,0)."""
        self._write_command(self.LCD_RETURNHOME)
        time.sleep_ms(3)  # Home command needs extra time
        self.cursor_x = 0
        self.cursor_y = 0

    def move_to(self, x, y):
        """Move cursor to specified position."""
        if x >= self.num_columns or y >= self.num_lines:
            print(f"Invalid move_to: x={x}, y={y} (max: {self.num_columns-1}x{self.num_lines-1})")
            return  # Ignore invalid positions

        self.cursor_x = x
        self.cursor_y = y

        # Set physical cursor position
        address = self._line_offsets[y] + x
        self._write_command(self.LCD_SETDDRAMADDR | address)

    def putchar(self, char):
        """Write a single character to the LCD."""
        if self.cursor_x >= self.num_columns:
            if self.cursor_y < self.num_lines - 1:
                # Move to next line
                self.move_to(0, self.cursor_y + 1)
            else:
                # Wrap to top
                self.move_to(0, 0)

        # Store in buffer and display
        self.buffer[self.cursor_y][self.cursor_x] = char

        # Set cursor position
        address = self._line_offsets[self.cursor_y] + self.cursor_x
        self._write_command(self.LCD_SETDDRAMADDR | address)

        # Write the character
        self._write_data(ord(char))
        self.cursor_x += 1

    def putstr(self, string):
        """Write a string to the LCD."""
        for char in string:
            if char == "\n":  # Handle newline character
                if self.cursor_y < self.num_lines - 1:
                    self.move_to(0, self.cursor_y + 1)
                else:
                    self.move_to(0, 0)
            else:
                self.putchar(char)

    def print_at(self, x, y, text):
        """Print text at specified position."""
        self.move_to(x, y)
        self.putstr(text)

    def create_char(self, location, charmap):
        """
        Store a custom character in CGRAM.

        Args:
            location: CGRAM location (0-7)
            charmap: Bytearray containing character bitmap (8 bytes)
        """
        location &= 0x07  # Only 8 locations (0-7) are available
        self._write_command(self.LCD_SETCGRAMADDR | (location << 3))
        for byte in charmap:
            self._write_data(byte)
        self.move_to(self.cursor_x, self.cursor_y)  # Return to previous position

    def set_display(self, on):
        """Turn the display on/off."""
        if on:
            self.display_control |= self.LCD_DISPLAYON
        else:
            self.display_control &= ~self.LCD_DISPLAYON
        self._write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def set_cursor(self, on):
        """Turn the cursor on/off."""
        if on:
            self.display_control |= self.LCD_CURSORON
        else:
            self.display_control &= ~self.LCD_CURSORON
        self._write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def set_blink(self, on):
        """Turn cursor blinking on/off."""
        if on:
            self.display_control |= self.LCD_BLINKON
        else:
            self.display_control &= ~self.LCD_BLINKON
        self._write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def scroll(self, direction=1, count=1):
        """
        Scroll display in specified direction.

        Args:
            direction: 1 for right, -1 for left
            count: Number of positions to scroll
        """
        command = self.LCD_CURSORSHIFT | 0x08
        if direction > 0:
            command |= 0x04  # Scroll right

        for _ in range(abs(count)):
            self._write_command(command)
            time.sleep_ms(1)

    def set_text_direction(self, left_to_right):
        """Set text direction (True for left-to-right)."""
        if left_to_right:
            self.display_mode = (self.display_mode & ~self.LCD_ENTRYRIGHT) | self.LCD_ENTRYLEFT
        else:
            self.display_mode = (self.display_mode & ~self.LCD_ENTRYLEFT) | self.LCD_ENTRYRIGHT
        self._write_command(self.LCD_ENTRYMODESET | self.display_mode)

    def set_autoscroll(self, on):
        """Enable/disable automatic scrolling."""
        if on:
            self.display_mode |= self.LCD_ENTRYSHIFTINCREMENT
        else:
            self.display_mode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self._write_command(self.LCD_ENTRYMODESET | self.display_mode)

    def set_backlight(self, on):
        """Turn backlight on/off."""
        self.backlight = self.LCD_BACKLIGHT if on else self.LCD_NOBACKLIGHT
        self._write_command(0x00)  # Send dummy command to update backlight

    def set_contrast(self, level):
        """
        Set display contrast (if supported by hardware).

        Args:
            level: Contrast level (0-255)
        """
        try:
            # Many I2C contrast controllers use register 0x2F
            self.i2c.writeto(self.i2c_addr, bytearray([0x2F, level]))
        except:
            pass  # Ignore if not supported

    def refresh(self):
        """Refresh the entire display from the buffer."""
        for y in range(self.num_lines):
            for x in range(self.num_columns):
                address = self._line_offsets[y] + x
                self._write_command(self.LCD_SETDDRAMADDR | address)
                self._write_data(ord(self.buffer[y][x]))

    def create_progress_bar(self, row, progress, width=None):
        """
        Create a progress bar on the specified row.

        Args:
            row: Row to display progress bar
            progress: Value between 0.0 and 1.0
            width: Width of progress bar (defaults to display width)
        """
        if width is None:
            width = self.num_columns

        # Create custom characters for progress bar if not already created
        if not hasattr(self, "_progress_chars_created"):
            self._create_progress_bar_chars()
            self._progress_chars_created = True

        filled_blocks = int(progress * width)
        remainder = int((progress * width - filled_blocks) * 5)

        self.move_to(0, row)
        # Draw full blocks
        for i in range(filled_blocks):
            self._write_data(255)  # Solid block character

        # Draw partial block for remainder
        if filled_blocks < width:
            if remainder > 0:
                self._write_data(remainder)  # Custom character (1-4)
            else:
                self._write_data(32)  # Space

            # Fill remaining with spaces
            for i in range(filled_blocks + 1, width):
                self._write_data(32)  # Space

    def _create_progress_bar_chars(self):
        """Create custom characters for progress bar visualization."""
        # Character 1: 1/5 filled
        self.create_char(
            1,
            bytearray([0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111])
        )

        # Character 2: 2/5 filled
        self.create_char(
            2,
            bytearray([0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111])
        )

        # Character 3: 3/5 filled
        self.create_char(
            3,
            bytearray([0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111, 0b11111])
        )

        # Character 4: 4/5 filled
        self.create_char(
            4,
            bytearray([0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111, 0b11111, 0b11111])
        )

    def scroll_text(self, row, text, delay=300, repeat=1):
        """
        Scroll text horizontally across a row.

        Args:
            row: Row to display scrolling text
            text: Text to scroll
            delay: Delay between scrolls in milliseconds
            repeat: Number of times to repeat (0 for infinite)
        """
        padded_text = " " * self.num_columns + text + " " * self.num_columns

        count = 0
        while repeat == 0 or count < repeat:
            for i in range(len(padded_text) - self.num_columns):
                self.move_to(0, row)
                self.putstr(padded_text[i:i + self.num_columns])
                time.sleep_ms(delay)
            count += 1

    def create_animation(self, row, frames, delay=200, repeat=1):
        """
        Create a simple animation by cycling through frames.

        Args:
            row: Row to display animation
            frames: List of strings to display in sequence
            delay: Delay between frames in milliseconds
            repeat: Number of times to repeat (0 for infinite)
        """
        count = 0
        while repeat == 0 or count < repeat:
            for frame in frames:
                self.move_to(0, row)
                # Pad or truncate frame to match display width
                if len(frame) < self.num_columns:
                    frame = frame + " " * (self.num_columns - len(frame))
                else:
                    frame = frame[:self.num_columns]
                self.putstr(frame)
                time.sleep_ms(delay)
            count += 1

    # Alias methods for backward compatibility
    def display_on(self):
        """Turn the display on."""
        self.set_display(True)

    def display_off(self):
        """Turn the display off."""
        self.set_display(False)

    def cursor_on(self):
        """Turn the cursor on."""
        self.set_cursor(True)

    def cursor_off(self):
        """Turn the cursor off."""
        self.set_cursor(False)

    def blink_on(self):
        """Turn cursor blinking on."""
        self.set_blink(True)

    def blink_off(self):
        """Turn cursor blinking off."""
        self.set_blink(False)

    def scroll_left(self):
        """Scroll display left."""
        self.scroll(-1)

    def scroll_right(self):
        """Scroll display right."""
        self.scroll(1)

    def left_to_right(self):
        """Set text to flow left to right."""
        self.set_text_direction(True)

    def right_to_left(self):
        """Set text to flow right to left."""
        self.set_text_direction(False)

    def autoscroll_on(self):
        """Enable automatic scrolling."""
        self.set_autoscroll(True)

    def autoscroll_off(self):
        """Disable automatic scrolling."""
        self.set_autoscroll(False)

    def backlight_on(self):
        """Turn backlight on."""
        self.set_backlight(True)

    def backlight_off(self):
        """Turn backlight off."""
        self.set_backlight(False)
