"""Height gradient effect - color gradient based on tree height."""

import numpy as np
from src.effect_base import Effect
from src.tree_model import TreeModel
from utils.color_utils import hsv_to_rgb, blend_colors
from typing import Tuple, List


class HeightGradientEffect(Effect):
    """Color gradient effect based on height in the tree."""

    def __init__(self, led_count: int, fps: int = 30, tree_model: TreeModel = None,
                 colors: List[Tuple[int, int, int]] = None,
                 animated: bool = True,
                 speed: float = 0.2,
                 **kwargs):
        """
        Initialize height gradient effect.

        Args:
            led_count: Number of LEDs
            fps: Frames per second
            tree_model: 3D tree model (required)
            colors: List of RGB colors for gradient (None for rainbow)
            animated: Whether to animate the gradient
            speed: Animation speed if animated
        """
        super().__init__(led_count, fps, tree_model, **kwargs)

        if tree_model is None:
            raise ValueError("HeightGradientEffect requires a tree_model")

        self.colors = colors
        self.animated = animated
        self.speed = speed

        # Get normalized heights for all LEDs
        self.heights = tree_model.get_height_normalized()

    def update(self, dt: float):
        """Update height gradient."""
        time_offset = self.get_time() * self.speed if self.animated else 0

        for i in range(self.led_count):
            # Get height with optional animation offset
            height = (self.heights[i] + time_offset) % 1.0

            if self.colors is None:
                # Rainbow gradient
                hue = height
                r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
            else:
                # Custom color gradient
                r, g, b = self._interpolate_colors(height)

            self.set_pixel(i, r, g, b)

    def _interpolate_colors(self, position: float) -> Tuple[int, int, int]:
        """
        Interpolate between custom colors based on position.

        Args:
            position: Position in gradient (0-1)

        Returns:
            RGB color tuple
        """
        if len(self.colors) == 1:
            return self.colors[0]

        # Find which color segment we're in
        segment_size = 1.0 / (len(self.colors) - 1)
        segment_idx = int(position / segment_size)
        segment_idx = min(segment_idx, len(self.colors) - 2)

        # Calculate position within segment
        segment_pos = (position - segment_idx * segment_size) / segment_size

        # Blend between colors
        color1 = self.colors[segment_idx]
        color2 = self.colors[segment_idx + 1]

        return blend_colors(color1, color2, segment_pos)
