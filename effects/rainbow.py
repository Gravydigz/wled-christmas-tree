"""Rainbow effect - classic rainbow cycling animation."""

import numpy as np
from src.effect_base import Effect
from utils.color_utils import wheel


class RainbowEffect(Effect):
    """Rainbow effect that cycles through all colors."""

    def __init__(self, led_count: int, fps: int = 30, speed: float = 1.0, **kwargs):
        """
        Initialize rainbow effect.

        Args:
            led_count: Number of LEDs
            fps: Frames per second
            speed: Speed multiplier (higher = faster)
        """
        super().__init__(led_count, fps, **kwargs)
        self.speed = speed
        self.offset = 0

    def update(self, dt: float):
        """Update rainbow animation."""
        # Increment offset based on time and speed
        self.offset += dt * self.speed * 50

        # Generate rainbow colors
        for i in range(self.led_count):
            pixel_index = int((i * 256 / self.led_count) + self.offset) % 256
            self.pixels[i] = wheel(pixel_index)
