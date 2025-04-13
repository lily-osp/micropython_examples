# I2C LCD Animation Library for MicroPython

## Overview

This library provides a comprehensive set of animations and display functions for HD44780-compatible LCD displays connected via I2C. It's designed for MicroPython on ESP8266/ESP32 boards but can be adapted for other platforms.

## Features

- **Basic Display Control**: Clear screen, cursor positioning, text display
- **Custom Characters**: Support for 8 user-defined 5x8 pixel characters
- **Scroll Animations**:
  - Left/right single-line scrolling
  - Dual-line scrolling with independent directions
- **Text Effects**:
  - Progressive character-by-character reveal
  - Blinking text
  - Bouncing text
- **Graphical Animations**:
  - Wave pattern
  - Checkerboard
  - Random character flashes
- **Backlight Control**: Pulsing and toggle effects
- **Combined Animations**: Layer simple effects for complex displays

## Hardware Requirements

- HD44780-compatible LCD with I2C backpack
- ESP8266 or ESP32 development board
- 4.7kΩ pull-up resistors on SDA/SCL lines (if not on backpack)

## Wiring

| LCD I2C | ESP8266/ESP32 |
| ------- | ------------- |
| GND     | GND           |
| VCC     | 5V/VIN        |
| SDA     | GPIO4 (D2)    |
| SCL     | GPIO5 (D1)    |

*Note: GPIO pins can be changed in configuration*

## Installation

1. Copy both files to your device:
   
   - `i2c_lcd.py` (LCD driver library)
   - `main.py` (Demo program)

2. The display should automatically start the demo sequence on boot.

## Usage

### Basic Setup

```python
from machine import SoftI2C, Pin
from i2c_lcd import I2cLcd

# Initialize I2C and LCD
i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=400000)
lcd = I2cLcd(i2c, 0x27, num_lines=2, num_columns=16)
```

### Running Animations

```python
from lcd_animations import LCDAnimations

# Single animation
LCDAnimations.scroll_left("Hello world!", row=0, delay=0.2)

# Combined animation
LCDAnimations.scroll_with_blink(
    scroll_text="System loading...",
    blink_text="Please wait",
    row=0,
    delay=0.3
)
```

## API Reference

### Core LCD Methods

- `clear()` - Clear the display
- `move_to(x, y)` - Position cursor
- `putstr(text)` - Write text at cursor
- `create_char(location, charmap)` - Define custom character
- `backlight_on()/off()` - Control backlight

### Animation Methods

#### Basic Text Animations

- `scroll_left(text, row, delay, clear)`
- `scroll_right(text, row, delay, clear)`
- `dual_scroll(text1, text2, dir1, dir2, delay)`
- `blink_text(text, row, times, delay)`
- `progressive_reveal(text, row, delay, clear)`
- `bounce_animation(text, row, delay, cycles)`

#### Graphical Effects

- `wave_animation(delay, cycles)`
- `checkerboard(delay, cycles)`
- `random_char_flash(times, delay)`
- `custom_char_showcase(delay)`

#### Backlight Effects

- `backlight_pulse(times, steps)`

#### Combined Animations

- `scroll_with_blink(scroll_text, blink_text, row, delay)`
- `wave_with_backlight(delay, cycles)`
- `bounce_with_progressive(bounce_text, reveal_text, delay)`

## Custom Characters

The library includes 8 predefined custom characters:

1. ❤ Heart
2. → Arrow
3. □ Box
4. ✓ Checkmark
5. ☺ Smiley
6. ★ Star
7. 🔔 Bell
8. █ Solid block

To define your own characters, modify the `CUSTOM_CHARS` array with 8-byte arrays representing the 5x8 pixel patterns.

## Example Demos

The `main.py` includes a comprehensive demo sequence that:

1. Shows basic scrolling in both directions
2. Demonstrates dual-direction scrolling
3. Displays all text effects
4. Runs graphical animations
5. Shows backlight effects
6. Demonstrates combined animations

## Troubleshooting

**Display not working?**

1. Verify I2C address (try 0x27 or 0x3F)
2. Check wiring connections
3. Ensure pull-up resistors are present
4. Try reducing I2C frequency

**Animations too fast/slow?**
Adjust the `delay` parameter in animation calls

**Custom characters not appearing?**
Verify your byte patterns exactly match the 5x8 format

## License

MIT License - Free for personal and commercial use

## Contributing

Contributions are welcome! Please open issues or pull requests for:

- New animation types
- Bug fixes
- Performance improvements
- Additional display controller support
