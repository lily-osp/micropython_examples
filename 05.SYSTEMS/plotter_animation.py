import time
import math
import random

# Simulating a manageable high frequency for better visualization
base_freq = 160

while True:
    for _ in range(20):  # Number of random waves to draw
        # Random frequency variation to avoid overly chaotic patterns
        freq_variation = random.uniform(-0.1, 0.1)
        freq = base_freq + freq_variation

        # Random amplitude between 20 and 60
        amplitude = random.uniform(20, 60)

        # Random phase shift between 0 and 2*pi
        phase_shift = random.uniform(0, 2 * math.pi)

        # X increment is more consistent to create a smoother wave
        x_increment = 0.1
        x = 0

        values = []
        for i in range(100):
            # Generate the wave value with slightly varied frequency, random amplitude, and phase shift
            y = 50 + amplitude * math.sin(freq * x + phase_shift)
            values.append(int(y))
            x += x_increment

        # Print the wave values to the serial plotter
        print(', '.join(map(str, values)))

        # Delay for a smooth animation
        time.sleep(0.1)
