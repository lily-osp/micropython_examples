# I2C LCD Animation Library for MicroPython

## Overview

This library provides a comprehensive set of animations and display functions for HD44780-compatible LCD displays connected via I2C adapters. Designed for MicroPython on ESP8266/ESP32 boards, the library offers advanced features like display rotation, custom characters, animations, progress bars, and buffer-based operations.

## Features

### Basic Display Control
- Clear screen, home cursor, position control
- Cursor style: visible/invisible, blinking/solid
- Text direction control (left-to-right, right-to-left)
- Display on/off and contrast control
- Backlight control with fading effects

### Advanced Display Features
- **Display Rotation**: 0°, 90°, 180°, and 270° rotation modes
- **Custom Characters**: Support for 8 user-defined 5x8 pixel characters
- **Progress Bars**: Adjustable width with partial block rendering
- **Text Buffer**: Store and manipulate display content in memory before rendering

### Animation System
- **Text Scrolling**:
  - Horizontal scrolling with configurable speed
  - Multi-line scrolling capabilities
  - Bounce effects with direction changes
- **Character Animations**:
  - Frame-by-frame animation sequences
  - Character-by-character text reveal
  - Custom character animations
- **Visual Effects**:
  - Checkerboard patterns
  - Wave animations
  - Backlight pulsing
  - Random character flash effects

## Hardware Requirements

- HD44780-compatible LCD with I2C backpack (PCF8574 or similar)
- ESP8266, ESP32, or other MicroPython-compatible board
- 4.7kΩ pull-up resistors on SDA/SCL lines (if not included on backpack)
- 5V power supply for the LCD display

## Wiring

| LCD I2C | ESP8266/ESP32 |
| ------- | ------------- |
| GND     | GND           |
| VCC     | 5V/VIN        |
| SDA     | GPIO4 (D2)    |
| SCL     | GPIO5 (D1)    |

*Note: GPIO pins are configurable in the code (see Configuration section)*

## Installation

1. Copy the library files to your MicroPython device:
   - `i2c_lcd.py` - Core LCD driver library
   - `main.py` - Demo program with animation examples

2. Ensure the files are in the root directory of your device.

3. The device will automatically run the demo on boot if `main.py` is present.

## Configuration

The default configuration can be modified in your application:

```python
# Default configuration (modify as needed)
I2C_SCL_PIN = 5  # GPIO5 (D1 on ESP8266)
I2C_SDA_PIN = 4  # GPIO4 (D2 on ESP8266)
I2C_FREQ = 400000  # 400kHz standard I2C frequency
I2C_ADDR = 0x27   # Common addresses: 0x27 or 0x3F
```

*Note: Run the diagnostic mode to scan for the correct I2C address if your display doesn't work with the default.*

## Usage Examples

### Basic Setup

```python
from machine import SoftI2C, Pin
from i2c_lcd import I2cLcd

# Initialize I2C and LCD
i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=400000)
lcd = I2cLcd(i2c, 0x27, num_lines=2, num_columns=16)

# Basic text display
lcd.clear()
lcd.print_at(0, 0, "Hello, World!")
```

### Custom Characters

```python
# Create a heart symbol
heart = bytearray([0x00, 0x0A, 0x1F, 0x1F, 0x0E, 0x04, 0x00, 0x00])
lcd.create_char(0, heart)

# Display the heart
lcd.move_to(0, 0)
lcd.putchar(chr(0))
```

### Display Rotation

```python
# Display rotation demonstration
lcd.clear()
lcd.print_at(0, 0, "Normal mode")
time.sleep(2)

# Rotate display 180 degrees
lcd.set_rotation(lcd.ROTATION_180)
lcd.clear()
lcd.print_at(0, 0, "Upside down!")
```

### Text Animation

```python
# Scrolling text animation
message = "This is a long scrolling message"
lcd.scroll_text(row=1, text=message, delay=200, repeat=2)

# Frame-by-frame animation
frames = ["Loading  ", "Loading .", "Loading..", "Loading..."]
lcd.create_animation(row=0, frames=frames, delay=300, repeat=3)
```

### Progress Bar

```python
# Create a progress bar
for i in range(21):
    progress = i / 20.0
    lcd.create_progress_bar(row=1, progress=progress)
    lcd.print_at(0, 0, f"Progress: {int(progress*100)}%")
    time.sleep(0.2)
```

## API Reference

### Constructor

- `I2cLcd(i2c, i2c_addr, num_lines=2, num_columns=16, char_size=LCD_5x8DOTS)`

### Basic Display Methods

- `clear()` - Clear the display
- `home()` - Return cursor to the home position (0,0)
- `move_to(x, y)` - Position cursor at coordinates
- `putchar(char)` - Write a single character at cursor position
- `putstr(string)` - Write a string at cursor position
- `print_at(x, y, text)` - Print text at specified position

### Display Control

- `set_display(on)` - Turn the display on/off
- `set_cursor(on)` - Show/hide the cursor
- `set_blink(on)` - Enable/disable cursor blinking
- `set_backlight(on)` - Turn the backlight on/off
- `set_contrast(level)` - Set display contrast (0-255, if supported)
- `set_rotation(rotation)` - Set display rotation (0°, 90°, 180°, 270°)
- `set_text_direction(left_to_right)` - Set text direction
- `set_autoscroll(on)` - Enable/disable automatic display scrolling

### Custom Characters

- `create_char(location, charmap)` - Create custom character at location (0-7)

### Animation Methods

- `scroll_text(row, text, delay, repeat)` - Scroll text horizontally
- `create_animation(row, frames, delay, repeat)` - Run frame-by-frame animation
- `create_progress_bar(row, progress, width)` - Display progress bar

### Display Buffer Methods

- `refresh()` - Update display from buffer
- Buffer can be accessed directly via `lcd.buffer[y][x]`

### Backward Compatibility Methods

The library includes aliases for older method names:
- `display_on()`, `display_off()`
- `cursor_on()`, `cursor_off()`
- `blink_on()`, `blink_off()`
- `backlight_on()`, `backlight_off()`
- `scroll_left()`, `scroll_right()`
- and more...

## Predefined Custom Characters

The demo includes 8 predefined custom characters:

1. ❤️ Heart
2. ➡️ Arrow
3. ▢ Box
4. ✓ Checkmark
5. ☺️ Smiley
6. ★ Star
7. 🔔 Bell
8. █ Solid block

## Diagnostic Mode

The library includes a diagnostic mode for troubleshooting:

```python
# Run diagnostics
run_diagnostics = True  # Set to True to enable diagnostic mode
```

Diagnostic features include:
- I2C bus scanning to find connected devices
- GPIO test to verify pin functionality
- Display pattern test to check all pixels
- Backlight testing

## Advanced Topics

### Creating Complex Animations

You can create more complex animations by combining the basic methods:

```python
def bounce_with_backlight():
    text = " * "
    pos = 0
    direction = 1
    for i in range(30):
        lcd.clear()
        lcd.print_at(pos, 0, text)
        lcd.set_backlight(i % 2 == 0)  # Blink backlight
        pos += direction
        if pos >= (16 - len(text)) or pos <= 0:
            direction = -direction
        time.sleep(0.2)
```

### Using the Buffer for Complex Displays

```python
# Create a checkerboard pattern using the buffer
for y in range(lcd.num_lines):
    for x in range(lcd.num_columns):
        lcd.buffer[y][x] = chr(7) if (x + y) % 2 == 0 else " "
lcd.refresh()  # Update display from buffer
```

## Troubleshooting

### Common Issues

**Display not working:**
1. Verify I2C address using diagnostic mode (common addresses: 0x27, 0x3F)
2. Check wiring connections and ensure proper power supply
3. Try reducing I2C frequency (e.g., to 100000)
4. Verify pull-up resistors are present on SDA/SCL lines

**Garbled display:**
1. Ensure proper initialization sequence
2. Check if display is actually HD44780 compatible
3. Try different contrast setting if available

**Animations not working:**
1. Verify display is functioning with basic commands first
2. Check for sufficient delays between frames
3. Ensure custom characters are properly loaded

### Debug Tips

Add diagnostic printing to help identify issues:

```python
# Add debugging
import sys
def debug(msg):
    print(msg)
    sys.stdout.flush()  # Ensure message is output immediately

# Use in code
debug(f"I2C devices found: {i2c.scan()}")
```

## Performance Optimization

- Reduce I2C frequency if experiencing reliability issues
- Minimize display updates by using the buffer
- Use delays appropriate for your microcontroller speed
- For smooth animations, keep frame changes small

## Contributing

Contributions to improve the library are welcome:

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

Areas for enhancement:
- New animation types
- Support for additional display controllers
- Performance optimizations
- Enhanced error handling

## License

MIT License - Free for personal and commercial use

## Acknowledgments

- Based on the HD44780 LCD datasheet
- Inspired by various MicroPython LCD libraries
- Special thanks to the MicroPython community
