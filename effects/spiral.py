"""Spiral effect - spiral pattern around the tree."""

import numpy as np
from src.effect_base import Effect
from src.tree_model import TreeModel
from utils.color_utils import hsv_to_rgb


class SpiralEffect(Effect):
    """Spiral effect that rotates around the tree."""

    def __init__(self, led_count: int, fps: int = 30, tree_model: TreeModel = None,
                 speed: float = 0.5,
                 rotations: float = 3.0,
                 width: float = 0.15,
                 **kwargs):
        """
        Initialize spiral effect.

        Args:
            led_count: Number of LEDs
            fps: Frames per second
            tree_model: 3D tree model (required)
            speed: Rotation speed (rotations per second)
            rotations: Number of spiral rotations up the tree
            width: Width of the spiral band (0-1)
        """
        super().__init__(led_count, fps, tree_model, **kwargs)

        if tree_model is None:
            raise ValueError("SpiralEffect requires a tree_model")

        self.speed = speed
        self.rotations = rotations
        self.width = width

        # Get heights and angles for all LEDs
        self.heights = tree_model.get_height_normalized()
        self.angles = tree_model.get_angle_from_center()

    def update(self, dt: float):
        """Update spiral animation."""
        time = self.get_time()

        # Calculate rotation offset
        rotation_offset = (time * self.speed * 2 * np.pi) % (2 * np.pi)

        for i in range(self.led_count):
            # Calculate expected angle for this height in the spiral
            expected_angle = (self.heights[i] * self.rotations * 2 * np.pi + rotation_offset) % (2 * np.pi)

            # Calculate angular distance
            angle_diff = abs(self.angles[i] - expected_angle)
            if angle_diff > np.pi:
                angle_diff = 2 * np.pi - angle_diff

            # Normalize to 0-1
            angle_diff_norm = angle_diff / np.pi

            # Brightness based on angular distance
            if angle_diff_norm < self.width:
                brightness = 1.0 - (angle_diff_norm / self.width)
                brightness = brightness ** 2
            else:
                brightness = 0.0

            # Color based on height
            hue = self.heights[i]
            r, g, b = hsv_to_rgb(hue, 1.0, brightness)
            self.set_pixel(i, r, g, b)
