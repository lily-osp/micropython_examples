from machine import I2C, Pin
from i2c_lcd import I2cLcd
import time
import urandom

class LCDDemo:
    """
    Comprehensive demonstration of the I2cLcd library capabilities.
    Contains various demos, animations and visual effects.
    """
    
    def __init__(self, i2c_scl_pin=22, i2c_sda_pin=21, i2c_freq=400000, 
                 i2c_addr=0x27, num_lines=4, num_columns=20):
        """Initialize the LCD demo with configurable parameters."""
        # Initialize I2C
        self.i2c = I2C(0, scl=Pin(i2c_scl_pin), sda=Pin(i2c_sda_pin), freq=i2c_freq)
        
        # Define line offsets based on display size
        if num_lines == 1:
            line_offsets = [0x00]
        elif num_lines == 2:
            line_offsets = [0x00, 0x40]
        elif num_lines == 4 and num_columns == 16:
            line_offsets = [0x00, 0x40, 0x10, 0x50]  # 16x4 LCD
        elif num_lines == 4 and num_columns == 20:
            line_offsets = [0x00, 0x40, 0x14, 0x54]  # 20x4 LCD
        else:
            # Default offsets for other configurations
            line_offsets = [0x00, 0x40, 0x14, 0x54]
        
        # Try to initialize LCD
        try:
            self.lcd = I2cLcd(self.i2c, i2c_addr, num_lines, num_columns, line_offsets)
            self.lcd.init_display()
            # Test all lines and columns
            self.test_display_size()
        except Exception as e:
            print(f"Failed to initialize LCD at address {hex(i2c_addr)}: {e}")
            self._scan_and_initialize(num_lines, num_columns, line_offsets)
            
        # Define custom characters
        self.CUSTOM_CHARS = [
            bytearray([0x00, 0x0A, 0x1F, 0x1F, 0x1F, 0x0E, 0x04, 0x00]),  # Heart (0)
            bytearray([0x04, 0x0E, 0x0E, 0x0E, 0x1F, 0x00, 0x04, 0x00]),  # Arrow (1)
            bytearray([0x1F, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1F, 0x00]),  # Box (2)
            bytearray([0x0E, 0x0E, 0x0E, 0x1F, 0x04, 0x04, 0x04, 0x00]),  # Checkmark (3)
            bytearray([0x0A, 0x1F, 0x1F, 0x00, 0x04, 0x0A, 0x11, 0x00]),  # Smiley (4)
            bytearray([0x00, 0x04, 0x0E, 0x1F, 0x0E, 0x04, 0x00, 0x00]),  # Diamond (5)
            bytearray([0x00, 0x04, 0x0E, 0x15, 0x0E, 0x04, 0x00, 0x00]),  # Star (6)
            bytearray([0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F]),  # Solid block (7)
        ]
        
        # Advanced animation sets
        self.SPINNER_FRAMES = [
            "|", "/", "-", "\\", "|", "/", "-", "\\"
        ]
        
        self.PACMAN_FRAMES = [
            ">. . . . . . . . . . . . . . . . . . .",
            " >. . . . . . . . . . . . . . . . . .",
            "  >. . . . . . . . . . . . . . . . . ",
            "   >. . . . . . . . . . . . . . . . .",
            "    >. . . . . . . . . . . . . . . . ",
            "     >. . . . . . . . . . . . . . . .",
            "      >. . . . . . . . . . . . . . . ",
            "       >. . . . . . . . . . . . . . .",
            "        >. . . . . . . . . . . . . . ",
            "         >. . . . . . . . . . . . . .",
            "          >. . . . . . . . . . . . . ",
            "           >. . . . . . . . . . . . .",
            "            >. . . . . . . . . . . . ",
            "             >. . . . . . . . . . . .",
            "              >. . . . . . . . . . . ",
            "             < . . . . . . . . . . . ",
            "            <. . . . . . . . . . . . ",
            "           <.. . . . . . . . . . . . ",
            "          <... . . . . . . . . . . . ",
            "         <.... . . . . . . . . . . . ",
            "        <..... . . . . . . . . . . . ",
            "       <...... . . . . . . . . . . . ",
            "      <....... . . . . . . . . . . . ",
            "     <........ . . . . . . . . . . . ",
            "    <......... . . . . . . . . . . . ",
            "   <.......... . . . . . . . . . . . ",
            "  <........... . . . . . . . . . . . ",
            " <............ . . . . . . . . . . . ",
            "<............. . . . . . . . . . . . "
        ]
        
        self.LOADING_FRAMES = [
            "[                    ]",
            "[=                   ]",
            "[==                  ]",
            "[===                 ]",
            "[====                ]",
            "[=====               ]",
            "[======              ]",
            "[=======             ]",
            "[========            ]",
            "[=========           ]",
            "[==========          ]",
        ]
        
        self.WAVE_FRAMES = [
            "~      ~      ~      ",
            " ~      ~      ~     ",
            "  ~      ~      ~    ",
            "   ~      ~      ~   ",
            "    ~      ~      ~  ",
            "     ~      ~      ~ ",
            "      ~      ~      ~",
            "       ~      ~      ",
        ]
        
        self.BOUNCE_FRAMES = [
            "o                   ",
            " o                  ",
            "  o                 ",
            "   o                ",
            "    o               ",
            "     o              ",
            "      o             ",
            "       o            ",
            "        o           ",
            "         o          ",
            "          o         ",
            "           o        ",
            "            o       ",
            "             o      ",
            "              o     ",
            "               o    ",
            "                o   ",
            "                 o  ",
            "                  o ",
            "                   o",
            "                  o ",
            "                 o  ",
            "                o   ",
            "               o    ",
            "              o     ",
            "             o      ",
            "            o       ",
            "           o        ",
            "          o         ",
            "         o          ",
            "        o           ",
            "       o            ",
            "      o             ",
            "     o              ",
            "    o               ",
            "   o                ",
            "  o                 ",
            " o                  ",
        ]
        
        # Load custom characters
        self._load_custom_chars()

    def test_display_size(self):
        """Test all lines and columns of the display."""
        self.lcd.clear()
        for y in range(self.lcd.num_lines):
            self.lcd.print_at(0, y, f"Line {y+1}: {'*' * self.lcd.num_columns}")
        print(f"Testing display: {self.lcd.num_columns}x{self.lcd.num_lines}")
        time.sleep(3)

    def _scan_and_initialize(self, num_lines, num_columns, line_offsets):
        """Scan I2C bus and try to initialize the LCD with detected addresses."""
        addresses = self.i2c.scan()
        if not addresses:
            raise RuntimeError("No I2C devices found! Check connections.")
            
        print(f"Found I2C devices at addresses: {[hex(addr) for addr in addresses]}")
        
        # Try each address
        for addr in addresses:
            try:
                print(f"Trying address {hex(addr)}...")
                self.lcd = I2cLcd(self.i2c, addr, num_lines, num_columns, line_offsets)
                self.lcd.init_display()
                self.lcd.clear()
                self.lcd.putstr("LCD Found!")
                self.test_display_size()
                return
            except Exception as e:
                print(f"Failed with address {hex(addr)}: {e}")
                
        raise RuntimeError("Could not initialize LCD with any detected I2C address")

    def _load_custom_chars(self):
        """Load all custom characters into CGRAM."""
        for i, char in enumerate(self.CUSTOM_CHARS):
            self.lcd.create_char(i, char)

    def welcome_screen(self):
        """Display welcome screen with version info."""
        self.lcd.clear()
        self.lcd.print_at(0, 0, f"LCD Demo v3.0 {self.lcd.num_columns}x{self.lcd.num_lines}")
        if self.lcd.num_lines > 2:
            self.lcd.print_at(0, 2, "Custom Chars:")
            for i in range(min(8, self.lcd.num_columns)):
                self.lcd.move_to(i, 3)
                self.lcd.putchar(chr(i))
                time.sleep(0.2)
        else:
            self.lcd.move_to(0, 1)
            for i in range(min(8, self.lcd.num_columns)):
                self.lcd.putchar(chr(i))
                time.sleep(0.2)
        time.sleep(1)
        self.lcd.print_at(0, self.lcd.num_lines-1, "Press Ctrl+C exit")
        time.sleep(2)

    def hardware_test(self):
        """Basic LCD hardware test."""
        # Test display on/off
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Display Test")
        time.sleep(1)

        self.lcd.set_display(False)
        time.sleep(1)
        self.lcd.set_display(True)
        time.sleep(1)

        # Test backlight
        self.lcd.print_at(0, 1, "Backlight Test")
        time.sleep(1)

        for _ in range(3):
            self.lcd.set_backlight(False)
            time.sleep(0.3)
            self.lcd.set_backlight(True)
            time.sleep(0.3)

        # Test cursor modes
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Cursor Test")

        # Normal cursor
        self.lcd.set_cursor(True)
        self.lcd.set_blink(False)
        self.lcd.print_at(0, 1, "Normal cursor")
        time.sleep(2)

        # Blinking cursor
        self.lcd.set_cursor(True)
        self.lcd.set_blink(True)
        self.lcd.print_at(0, 1, "Blinking cursor")
        time.sleep(2)

        # Turn off cursor
        self.lcd.set_cursor(False)
        self.lcd.set_blink(False)

    def text_direction_demo(self):
        """Demonstrate left-to-right and right-to-left text."""
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Text Direction")
        time.sleep(1)

        # Left to right (default)
        self.lcd.clear()
        self.lcd.set_text_direction(True)
        self.lcd.print_at(0, 0, "Left to Right")
        self.lcd.move_to(0, 1)
        for c in "12345":
            self.lcd.putchar(c)
            time.sleep(0.3)
        if self.lcd.num_lines > 2:
            self.lcd.print_at(0, 2, "Demo on all lines")
            self.lcd.print_at(0, 3, "1234567890" + "X" * (self.lcd.num_columns-10))
        time.sleep(1)

        # Right to left
        self.lcd.clear()
        self.lcd.set_text_direction(False)
        self.lcd.print_at(0, 0, "Right to Left")
        start_pos = self.lcd.num_columns - 1
        self.lcd.move_to(start_pos, 1)
        for c in "12345":
            self.lcd.putchar(c)
            time.sleep(0.3)
        if self.lcd.num_lines > 2:
            self.lcd.print_at(0, 2, "RTL on all lines")
            self.lcd.print_at(0, 3, "0987654321" + "Y" * (self.lcd.num_columns-10))
        time.sleep(1)

        # Reset to left-to-right
        self.lcd.set_text_direction(True)

    def scroll_demo(self):
        """Demonstrate various scrolling features."""
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Scroll Demo")
        time.sleep(1)

        # Using the scroll method
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Display scroll")
        self.lcd.print_at(0, 1, "Left <-> Right")
        if self.lcd.num_lines > 2:
            self.lcd.print_at(0, 2, "Line 3 Scroll")
            self.lcd.print_at(0, 3, "Line 4 Scroll")
        time.sleep(1)

        # Scroll right
        for _ in range(5):
            self.lcd.scroll(1)
            time.sleep(0.3)

        # Scroll left
        for _ in range(10):
            self.lcd.scroll(-1)
            time.sleep(0.3)

        # Scroll right to center again
        for _ in range(5):
            self.lcd.scroll(1)
            time.sleep(0.3)

        # Text scrolling
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Text scrolling:")
        time.sleep(1)

        long_text = "This is a scrolling message demonstrating the text scrolling feature of the LCD library"
        self.lcd.scroll_text(1, long_text, delay=200, repeat=1)
        if self.lcd.num_lines > 2:
            self.lcd.scroll_text(3, long_text, delay=200, repeat=1)

    def progress_bar_demo(self):
        """Demonstrate progress bar functionality."""
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Progress Bar")

        # Show progress from 0 to 100%
        steps = 20
        for i in range(steps + 1):
            progress = i / steps
            self.lcd.create_progress_bar(1, progress)
            self.lcd.move_to(0, 0)
            self.lcd.putstr(f"Progress: {int(progress*100):3d}%")
            if self.lcd.num_lines > 2:
                self.lcd.create_progress_bar(3, progress)
            time.sleep(0.2)

        time.sleep(1)

    def custom_char_showcase(self):
        """Show all custom characters with labels."""
        names = ["Heart", "Arrow", "Box", "Check", 
                "Smile", "Diamond", "Star", "Block"]
                
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Custom Chars:")

        for i, name in enumerate(names):
            self.lcd.clear()
            self.lcd.print_at(0, 0, f"Char {i}: {name}")
            self.lcd.move_to(8, 1)
            self.lcd.putchar(chr(i))
            if self.lcd.num_lines > 2:
                self.lcd.print_at(0, 2, f"Char {i} on Line 3")
                self.lcd.move_to(8, 3)
                self.lcd.putchar(chr(i))
            time.sleep(1)

    def buffer_demo(self):
        """Demonstrate buffer-based operations."""
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Buffer Demo")
        time.sleep(1)

        # Fill the buffer with pattern
        for y in range(self.lcd.num_lines):
            for x in range(self.lcd.num_columns):
                self.lcd.buffer[y][x] = chr((x + y) % 8)  # Use custom chars

        # Refresh to display buffer contents
        self.lcd.refresh()
        time.sleep(2)

        # Modify buffer and refresh again
        for y in range(self.lcd.num_lines):
            for x in range(self.lcd.num_columns):
                if (x + y) % 2 == 0:
                    self.lcd.buffer[y][x] = " "

        self.lcd.refresh()
        time.sleep(2)

    def spinner_animation(self):
        """Show a spinner animation."""
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Spinner Animation")
        
        x_pos = self.lcd.num_columns // 2
        y_pos = 1
        y_pos2 = 3 if self.lcd.num_lines > 2 else 1
        
        # Run the spinner animation
        for _ in range(16):
            for frame in self.SPINNER_FRAMES:
                self.lcd.move_to(x_pos, y_pos)
                self.lcd.putchar(frame)
                if self.lcd.num_lines > 2:
                    self.lcd.move_to(x_pos, y_pos2)
                    self.lcd.putchar(frame)
                time.sleep(0.1)

    def pacman_animation(self):
        """Display a Pacman-like animation."""
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Pacman Animation")
        
        # Use built-in animation method
        self.lcd.create_animation(1, self.PACMAN_FRAMES, delay=150, repeat=1)
        if self.lcd.num_lines > 2:
            self.lcd.create_animation(3, self.PACMAN_FRAMES, delay=150, repeat=1)

    def loading_bar_animation(self):
        """Show an animated loading bar."""
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Loading Animation")
        
        # Use built-in animation method
        self.lcd.create_animation(1, self.LOADING_FRAMES, delay=200, repeat=1)
        if self.lcd.num_lines > 2:
            self.lcd.create_animation(3, self.LOADING_FRAMES, delay=200, repeat=1)

    def wave_animation(self):
        """Show a wave animation."""
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Wave Animation")
        
        # Use built-in animation method
        self.lcd.create_animation(1, self.WAVE_FRAMES, delay=150, repeat=2)
        if self.lcd.num_lines > 2:
            self.lcd.create_animation(3, self.WAVE_FRAMES, delay=150, repeat=2)

    def bounce_animation(self):
        """Show a bouncing ball animation."""
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Bounce Animation")
        
        # Use built-in animation method
        self.lcd.create_animation(1, self.BOUNCE_FRAMES, delay=100, repeat=1)
        if self.lcd.num_lines > 2:
            self.lcd.create_animation(3, self.BOUNCE_FRAMES, delay=100, repeat=1)

    def matrix_effect(self):
        """Create a Matrix-like rain effect."""
        self.lcd.clear()
        self.lcd.print_at(0, 0, "Matrix Effect")
        time.sleep(1)
        
        self.lcd.clear()
        cols = []
        
        # Initialize random columns
        for x in range(self.lcd.num_columns):
            cols.append(urandom.randint(0, self.lcd.num_lines * 3))
            
        # Run animation
        for _ in range(40):
            # Clear buffer
            for y in range(self.lcd.num_lines):
                for x in range(self.lcd.num_columns):
                    self.lcd.buffer[y][x] = " "
            
            # Update columns and buffer
            for x in range(self.lcd.num_columns):
                # Move down
                cols[x] += 1
                if cols[x] > self.lcd.num_lines * 3:
                    cols[x] = 0
                
                # Draw character if in visible range
                if 0 <= cols[x] < self.lcd.num_lines:
                    self.lcd.buffer[cols[x]][x] = chr(urandom.randint(0, 7))
                    
                # Draw trace (dimming characters behind)
                for trail in range(1, 3):
                    trail_pos = cols[x] - trail
                    if 0 <= trail_pos < self.lcd.num_lines:
                        # Use box character (2) for trail
                        self.lcd.buffer[trail_pos][x] = chr(2)
                        
            # Refresh display
            self.lcd.refresh()
            time.sleep(0.1)

    def run_all_demos(self):
        """Run all demos in sequence."""
        demos = [
            self.welcome_screen,
            self.hardware_test,
            self.text_direction_demo,
            self.scroll_demo,
            self.progress_bar_demo,
            self.custom_char_showcase,
            self.buffer_demo,
            self.spinner_animation,
            self.pacman_animation,
            self.loading_bar_animation,
            self.wave_animation,
            self.bounce_animation,
            self.matrix_effect
        ]

        try:
            while True:
                for demo in demos:
                    demo()
                    time.sleep(0.5)

                # Final message before looping
                self.lcd.clear()
                self.lcd.print_at(0, 0, "Demo completed")
                self.lcd.print_at(0, 1, "Restarting...")
                if self.lcd.num_lines > 2:
                    self.lcd.print_at(0, 3, f"{self.lcd.num_columns}x{self.lcd.num_lines} Display")
                time.sleep(2)

        except KeyboardInterrupt:
            # Clean exit with Ctrl+C
            self.lcd.clear()
            self.lcd.print_at(0, 0, "Demo stopped")
            time.sleep(1)
            self.lcd.clear()
            self.lcd.set_backlight(False)


def i2c_scanner():
    """Standalone utility to scan I2C bus and find devices."""
    try:
        i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        print("Using hardware I2C...")
    except:
        from machine import SoftI2C
        i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)
        print("Using software I2C...")
    
    print("Scanning I2C bus...")
    devices = i2c.scan()
    
    if devices:
        print(f"Found {len(devices)} I2C devices:")
        for device in devices:
            print(f"  - Address: {hex(device)} (decimal: {device})")
        
        print("\nCommon I2C LCD addresses:")
        print("  - 0x27 (most common PCF8574 backpack)")
        print("  - 0x3F (alternative PCF8574 backpack)")
        print("  - 0x20-0x27 (PCF8574 range)")
        print("  - 0x38-0x3F (PCF8574A range)")
    else:
        print("No I2C devices found! Check your connections.")
        
    return devices


if __name__ == "__main__":
    try:
        # Run I2C scanner to verify address
        i2c_scanner()
        
        # Create demo for 20x4 LCD
        demo = LCDDemo(i2c_scl_pin=22, i2c_sda_pin=21, i2c_addr=0x27, 
                      num_lines=4, num_columns=20)
        
        # Run all demos
        demo.run_all_demos()
        
    except Exception as e:
        print(f"Error: {e}")
        
        # Try to display error on LCD if possible
        try:
            if 'demo' in locals() and hasattr(demo, 'lcd'):
                demo.lcd.clear()
                demo.lcd.print_at(0, 0, "Error:")
                
                # Truncate error message to fit on display
                error_msg = str(e)
                max_len = demo.lcd.num_columns
                if len(error_msg) > max_len:
                    error_msg = error_msg[:max_len-3] + "..."
                    
                demo.lcd.print_at(0, 1, error_msg)
                time.sleep(5)
                demo.lcd.clear()
                demo.lcd.set_backlight(False)
        except:
            pass
        
        # Re-raise for debugging
        raise
