from machine import I2C
import time

class I2cLcd:
    # Constants for LCD commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80
    
    # Flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00
    
    # Flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00
    
    # Flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00
    
    # Flags for backlight control
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00
    
    # Control bits
    ENABLE = 0x04
    RS_DATA = 0x01
    RS_COMMAND = 0x00

    def __init__(self, i2c, i2c_addr, num_lines=2, num_columns=16, char_size=LCD_5x8DOTS):
        """
        Initialize the LCD.
        
        Args:
            i2c: I2C bus object
            i2c_addr: I2C address of the LCD
            num_lines: Number of display lines (1 or 2)
            num_columns: Number of characters per line
            char_size: Character size (LCD_5x8DOTS or LCD_5x10DOTS)
        """
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0
        self.backlight = self.LCD_BACKLIGHT
        self.display_control = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.display_function = self.LCD_4BITMODE | self.LCD_2LINE if num_lines > 1 else self.LCD_1LINE
        self.display_function |= char_size
        
        self._init_display()

    def _init_display(self):
        """Initialize the display in 4-bit mode."""
        # Wait for LCD to power on
        time.sleep_ms(50)
        
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
        self._write_command(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT)
        
        # Turn on display with configured settings
        self.display_on()

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

    def home(self):
        """Return cursor to home position (0,0)."""
        self._write_command(self.LCD_RETURNHOME)
        time.sleep_ms(3)  # Home command needs extra time
        self.cursor_x = 0
        self.cursor_y = 0

    def move_to(self, x, y):
        """Move cursor to specified position."""
        if x >= self.num_columns or y >= self.num_lines:
            return  # Ignore invalid positions
        
        self.cursor_x = x
        self.cursor_y = y
        
        # Calculate DDRAM address based on line offsets
        line_offsets = [0x00, 0x40, 0x14, 0x54]  # For 16x2, 20x4 displays
        address = line_offsets[y] + x
        self._write_command(self.LCD_SETDDRAMADDR | address)

    def putchar(self, char):
        """Write a single character to the LCD."""
        if self.cursor_x >= self.num_columns:
            return  # Don't write beyond display width
        self._write_data(ord(char))
        self.cursor_x += 1

    def putstr(self, string):
        """Write a string to the LCD."""
        for char in string:
            self.putchar(char)

    def create_char(self, location, charmap):
        """Store a custom character in CGRAM.
        
        Args:
            location: CGRAM location (0-7)
            charmap: Bytearray containing character bitmap (8 bytes)
        """
        location &= 0x07  # Only 8 locations (0-7) are available
        self._write_command(self.LCD_SETCGRAMADDR | (location << 3))
        for byte in charmap:
            self._write_data(byte)
        self.move_to(self.cursor_x, self.cursor_y)  # Return to previous position

    def display_on(self):
        """Turn the display on."""
        self.display_control |= self.LCD_DISPLAYON
        self._write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def display_off(self):
        """Turn the display off."""
        self.display_control &= ~self.LCD_DISPLAYON
        self._write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def cursor_on(self):
        """Turn the cursor on."""
        self.display_control |= self.LCD_CURSORON
        self._write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def cursor_off(self):
        """Turn the cursor off."""
        self.display_control &= ~self.LCD_CURSORON
        self._write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def blink_on(self):
        """Turn cursor blinking on."""
        self.display_control |= self.LCD_BLINKON
        self._write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def blink_off(self):
        """Turn cursor blinking off."""
        self.display_control &= ~self.LCD_BLINKON
        self._write_command(self.LCD_DISPLAYCONTROL | self.display_control)

    def scroll_left(self):
        """Scroll display left without changing RAM."""
        self._write_command(self.LCD_CURSORSHIFT | 0x08)

    def scroll_right(self):
        """Scroll display right without changing RAM."""
        self._write_command(self.LCD_CURSORSHIFT | 0x0C)

    def left_to_right(self):
        """Set text to flow left to right."""
        self.display_mode = self.LCD_ENTRYLEFT
        self._write_command(self.LCD_ENTRYMODESET | self.display_mode)

    def right_to_left(self):
        """Set text to flow right to left."""
        self.display_mode = self.LCD_ENTRYRIGHT
        self._write_command(self.LCD_ENTRYMODESET | self.display_mode)

    def autoscroll_on(self):
        """Enable automatic scrolling."""
        self.display_mode |= self.LCD_ENTRYSHIFTINCREMENT
        self._write_command(self.LCD_ENTRYMODESET | self.display_mode)

    def autoscroll_off(self):
        """Disable automatic scrolling."""
        self.display_mode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self._write_command(self.LCD_ENTRYMODESET | self.display_mode)

    def backlight_on(self):
        """Turn backlight on."""
        self.backlight = self.LCD_BACKLIGHT
        self._write_command(0x00)  # Send dummy command to update backlight

    def backlight_off(self):
        """Turn backlight off."""
        self.backlight = self.LCD_NOBACKLIGHT
        self._write_command(0x00)  # Send dummy command to update backlight

    def set_backlight(self, value):
        """Set backlight on/off with boolean."""
        self.backlight = self.LCD_BACKLIGHT if value else self.LCD_NOBACKLIGHT
        self._write_command(0x00)  # Send dummy command to update backlight