"""Rotating plane effect - a plane of light rotating through the tree."""

import numpy as np
from src.effect_base import Effect
from src.tree_model import TreeModel
from utils.color_utils import hsv_to_rgb


class RotatingPlaneEffect(Effect):
    """A plane of light that rotates around the tree's center axis."""

    def __init__(self, led_count: int, fps: int = 30, tree_model: TreeModel = None,
                 speed: float = 0.3,
                 thickness: float = 0.15,
                 **kwargs):
        """
        Initialize rotating plane effect.

        Args:
            led_count: Number of LEDs
            fps: Frames per second
            tree_model: 3D tree model (required)
            speed: Rotation speed (rotations per second)
            thickness: Thickness of the plane (radians)
        """
        super().__init__(led_count, fps, tree_model, **kwargs)

        if tree_model is None:
            raise ValueError("RotatingPlaneEffect requires a tree_model")

        self.speed = speed
        self.thickness = thickness

        # Get angles and heights for all LEDs
        self.angles = tree_model.get_angle_from_center()
        self.heights = tree_model.get_height_normalized()

    def update(self, dt: float):
        """Update rotating plane animation."""
        time = self.get_time()

        # Current plane angle
        plane_angle = (time * self.speed * 2 * np.pi) % (2 * np.pi)

        for i in range(self.led_count):
            # Calculate angular difference from plane
            angle_diff = abs(self.angles[i] - plane_angle)
            if angle_diff > np.pi:
                angle_diff = 2 * np.pi - angle_diff

            # Brightness based on distance from plane
            if angle_diff < self.thickness:
                brightness = 1.0 - (angle_diff / self.thickness)
                brightness = brightness ** 2
            else:
                brightness = 0.0

            # Color based on height
            hue = self.heights[i]
            r, g, b = hsv_to_rgb(hue, 1.0, brightness)
            self.set_pixel(i, r, g, b)
