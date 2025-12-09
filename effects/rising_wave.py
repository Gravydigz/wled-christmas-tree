"""Rising wave effect - wave that travels up the tree."""

import numpy as np
from src.effect_base import Effect
from src.tree_model import TreeModel
from utils.color_utils import hsv_to_rgb


class RisingWaveEffect(Effect):
    """Wave effect that rises up the tree based on Z-coordinate."""

    def __init__(self, led_count: int, fps: int = 30, tree_model: TreeModel = None,
                 speed: float = 0.3,
                 wave_height: float = 0.2,
                 hue: float = 0.5,
                 **kwargs):
        """
        Initialize rising wave effect.

        Args:
            led_count: Number of LEDs
            fps: Frames per second
            tree_model: 3D tree model (required)
            speed: Wave speed (cycles per second)
            wave_height: Height of wave relative to tree (0-1)
            hue: Base hue for the wave (0-1)
        """
        super().__init__(led_count, fps, tree_model, **kwargs)

        if tree_model is None:
            raise ValueError("RisingWaveEffect requires a tree_model")

        self.speed = speed
        self.wave_height = wave_height
        self.hue = hue

        # Get normalized heights for all LEDs
        self.heights = tree_model.get_height_normalized()

    def update(self, dt: float):
        """Update rising wave animation."""
        time = self.get_time()

        # Calculate wave position (0-1, repeating)
        wave_pos = (time * self.speed) % 1.0

        for i in range(self.led_count):
            # Calculate distance from wave center
            height = self.heights[i]
            dist_from_wave = abs(height - wave_pos)

            # Brightness based on distance from wave
            if dist_from_wave < self.wave_height:
                brightness = 1.0 - (dist_from_wave / self.wave_height)
                brightness = brightness ** 2  # Make it more focused
            else:
                brightness = 0.0

            r, g, b = hsv_to_rgb(self.hue, 1.0, brightness)
            self.set_pixel(i, r, g, b)
