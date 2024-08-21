from machine import Pin, I2C
import ssd1306
import time

# Function to scroll text
def scroll_text(display, text):
    for i in range(len(text) * 8):
        display.fill(0)
        display.text(text, -i, 3, 1)
        display.show()
        time.sleep(0.01)

# Initialize I2C and SSD1306 display
i2c = I2C(sda=Pin(21), scl=Pin(22))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# Multiple lines of text
lines = [
    "This is line 1",
    "This is line 2",
    "This is line 3",
    "This is line 4",
    "This is line 5"
]

# Display and scroll each line
for line in lines:
    scroll_text(display, line)
    time.sleep(0.5)  # Pause between lines

# Clear the display
display.fill(0)
display.show()
