import machine
import math

class WaveformGenerator:
    def __init__(self, pin, sample_rate=32000, amplitude=1.0):
        self.output_pin = machine.Pin(pin, machine.Pin.OUT)
        self.dac = machine.DAC(self.output_pin)
        self.sample_rate = sample_rate
        self.amplitude = amplitude
        self.waveform_functions = {
            "sine": self._sine_wave,
            "sawtooth": self._sawtooth_wave,
            "square": self._square_wave,
            "triangle": self._triangle_wave
        }
        self.sample_time = 1 / self.sample_rate

    def _sine_wave(self, time):
        """Calculate the value of a sine wave at the given time."""
        return int(127.5 + 127.5 * self.amplitude * math.sin(2 * math.pi * time))

    def _sawtooth_wave(self, time):
        """Calculate the value of a sawtooth wave at the given time."""
        return int(255 * self.amplitude * (time - math.floor(time)))

    def _square_wave(self, time):
        """Calculate the value of a square wave at the given time."""
        return 255 if math.sin(2 * math.pi * time) >= 0 else 0

    def _triangle_wave(self, time):
        """Calculate the value of a triangle wave at the given time."""
        return int(255 * self.amplitude * (2 * abs(2 * (time - math.floor(time + 0.5))) - 1))

    def generate_waveform(self, waveform_type, duration=1.0):
        """Generate a waveform of the specified type for the given duration."""
        current_time = 0
        waveform_function = self.waveform_functions[waveform_type]
        while current_time < duration:
            value = waveform_function(current_time)
            self.dac.write(max(0, min(255, value)))  # Adjusted for 8-bit DAC
            print(value)
            current_time += self.sample_time

    def run(self, waveform_type, duration=1.0):
        """Run the waveform generator for the specified type and duration."""
        self.generate_waveform(waveform_type, duration)

# Usage example
waveform_generator = WaveformGenerator(pin=25, sample_rate=32000, amplitude=0.5)
waveform_generator.run("triangle", duration=2.0)
