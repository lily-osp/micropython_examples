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
    bytearray([0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F])   # Solid block (7)
]

def load_custom_chars():
    """Load all custom characters into CGRAM."""
    for i, char in enumerate(CUSTOM_CHARS):
        lcd.create_char(i, char)

class LCDAnimations:
    @staticmethod
    def scroll_text(text, row=0, direction="left", delay=0.2, clear=True):
        """Scroll text horizontally on specified row."""
        if clear:
            lcd.move_to(0, row)
            lcd.putstr(" " * 16)
        
        padded = " " * 16 + text + " " * 16
        length = len(padded)
        range_args = (length - 15, -1, -1) if direction == "right" else range(length - 15)
        
        for i in range_args:
            lcd.move_to(0, row)
            lcd.putstr(padded[i:i+16])
            time.sleep(delay)

    @staticmethod
    def dual_scroll(text1, text2, delay=0.2):
        """Scroll different texts on both lines simultaneously."""
        pad = " " * 16
        texts = [pad + text1 + pad, pad + text2 + pad]
        max_len = max(len(t) for t in texts)
        
        for i in range(max_len - 15):
            for row in range(2):
                if i < len(texts[row]) - 15:
                    lcd.move_to(0, row)
                    lcd.putstr(texts[row][i:i+16])
            time.sleep(delay)

    @staticmethod
    def blink_text(text, row=0, times=3, delay=0.5):
        """Blink text on and off."""
        for _ in range(times):
            lcd.move_to(0, row)
            lcd.putstr(text)
            time.sleep(delay)
            lcd.move_to(0, row)
            lcd.putstr(" " * len(text))
            time.sleep(delay)
        lcd.move_to(0, row)
        lcd.putstr(text)

    @staticmethod
    def progressive_reveal(text, row=0, delay=0.1, clear=True):
        """Reveal text one character at a time."""
        if clear:
            lcd.move_to(0, row)
            lcd.putstr(" " * 16)
        
        lcd.move_to(0, row)
        for i, char in enumerate(text[:16]):  # Ensure we don't exceed display width
            lcd.putstr(char)
            time.sleep(delay)

    @staticmethod
    def custom_char_showcase(delay=0.8):
        """Show all custom characters with labels."""
        names = ["Heart", "Arrow", "Box", "Check", "Smiley", "Star", "Bell", "Block"]
        lcd.clear()
        
        for i, name in enumerate(names):
            lcd.move_to(0, 0)
            lcd.putstr(f"Char {i}:{chr(i)}")
            lcd.move_to(0, 1)
            lcd.putstr(name)
            time.sleep(delay)
        
        lcd.clear()

    @staticmethod
    def wave_animation(delay=0.15, cycles=2):
        """Wave animation with stars and smileys."""
        for _ in range(cycles):
            for col in range(16):
                for row, char in [(0, chr(5)), (1, chr(4))]:
                    lcd.move_to(col if row == 0 else 15-col, row)
                    lcd.putstr(char)
                    time.sleep(delay)
                    lcd.move_to(col if row == 0 else 15-col, row)
                    lcd.putstr(" ")
            lcd.clear()

    @staticmethod
    def checkerboard(delay=0.3, cycles=3):
        """Checkerboard pattern animation."""
        for _ in range(cycles):
            for pattern in [0, 1]:
                lcd.clear()
                for row in range(2):
                    for col in range(0, 16, 2):
                        pos = col + ((row + pattern) % 2)
                        lcd.move_to(pos, row)
                        lcd.putstr(chr(2 if pattern == 0 else 7))
                time.sleep(delay)
        lcd.clear()

    @staticmethod
    def backlight_pulse(times=3, steps=5):
        """Simulate backlight pulsing effect."""
        lcd.move_to(0, 0)
        lcd.putstr("Backlight Test")
        
        for _ in range(times):
            for direction in [1, -1]:  # 1 = fade in, -1 = fade out
                for i in range(steps)[::direction]:
                    lcd.backlight_on() if i > steps//2 else lcd.backlight_off()
                    time.sleep(0.05 * (steps - i if direction == 1 else i + 1))
        
        lcd.backlight_on()
        lcd.clear()

    @staticmethod
    def bounce_animation(text, row=0, delay=0.15, cycles=2):
        """Bounce text back and forth."""
        max_pos = 16 - len(text)
        
        for _ in range(cycles):
            for direction in [1, -1]:  # 1 = right, -1 = left
                for pos in range(max_pos)[::direction]:
                    lcd.move_to(pos, row)
                    lcd.putstr(text)
                    time.sleep(delay)
                    lcd.move_to(pos, row)
                    lcd.putstr(" " * len(text))
        
        lcd.move_to(0, row)
        lcd.putstr(text)

    @staticmethod
    def random_char_flash(times=20, delay=0.1):
        """Random character flash effect."""
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Random Flash")
        
        for _ in range(times):
            row = urandom.getrandbits(1)
            col = urandom.getrandbits(4)
            char = chr(urandom.getrandbits(3))
            
            lcd.move_to(col, row)
            lcd.putstr(char)
            time.sleep(delay)
            lcd.move_to(col, row)
            lcd.putstr(" ")
        
        lcd.clear()

    @staticmethod
    def run_demo_sequence():
        """Run a sequence of all animations."""
        animations = [
            ("Scrolling Text", lambda: LCDAnimations.scroll_text("Hello, ESP8266! LCD Demo", 0)),
            ("Dual Scroll", lambda: LCDAnimations.dual_scroll("Line 1 Scroll", "Line 2 Scroll")),
            ("Blinking Text", lambda: LCDAnimations.blink_text("Blink!", 1, 4)),
            ("Progressive Text", lambda: LCDAnimations.progressive_reveal("One by one", 0)),
            ("Custom Chars", LCDAnimations.custom_char_showcase),
            ("Wave Animation", lambda: LCDAnimations.wave_animation(cycles=3)),
            ("Checkerboard", lambda: LCDAnimations.checkerboard(cycles=3)),
            ("Backlight Pulse", lambda: LCDAnimations.backlight_pulse(times=2)),
            ("Bounce Effect", lambda: LCDAnimations.bounce_animation("BOUNCE", 0, cycles=2)),
            ("Random Flash", lambda: LCDAnimations.random_char_flash(times=30)),
        ]
        
        try:
            while True:
                for name, animation in animations:
                    lcd.clear()
                    lcd.move_to(0, 0)
                    lcd.putstr(name)
                    time.sleep(1.5)
                    animation()
                    time.sleep(1)
        except KeyboardInterrupt:
            lcd.clear()
            lcd.backlight_off()

if __name__ == "__main__":
    try:
        lcd.backlight_on()
        load_custom_chars()
        
        # Show welcome message
        lcd.move_to(0, 0)
        lcd.putstr("LCD Animations")
        lcd.move_to(0, 1)
        lcd.putstr("Press Ctrl+C")
        time.sleep(2)
        
        # Run the demo
        LCDAnimations.run_demo_sequence()
        
    except KeyboardInterrupt:
        lcd.clear()
        lcd.backlight_off()
    except Exception as e:
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Error:")
        lcd.move_to(0, 1)
        lcd.putstr(str(e)[:16])
        time.sleep(3)
        lcd.clear()
        lcd.backlight_off()
