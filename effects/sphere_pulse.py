"""Sphere pulse effect - expanding spheres from various points."""

import numpy as np
from src.effect_base import Effect
from src.tree_model import TreeModel
from utils.color_utils import hsv_to_rgb


class SpherePulseEffect(Effect):
    """Pulsing sphere effect emanating from points in the tree."""

    def __init__(self, led_count: int, fps: int = 30, tree_model: TreeModel = None,
                 speed: float = 0.5,
                 pulse_width: float = 0.1,
                 num_pulses: int = 3,
                 **kwargs):
        """
        Initialize sphere pulse effect.

        Args:
            led_count: Number of LEDs
            fps: Frames per second
            tree_model: 3D tree model (required)
            speed: Pulse speed (pulses per second)
            pulse_width: Width of pulse ring (relative to tree size)
            num_pulses: Number of simultaneous pulses
        """
        super().__init__(led_count, fps, tree_model, **kwargs)

        if tree_model is None:
            raise ValueError("SpherePulseEffect requires a tree_model")

        self.speed = speed
        self.pulse_width = pulse_width
        self.num_pulses = num_pulses

        # Calculate max distance for normalization
        self.max_distance = self._calculate_max_distance()

        # Generate random pulse origins
        self.pulse_origins = []
        for _ in range(num_pulses):
            idx = np.random.randint(0, led_count)
            self.pulse_origins.append(tree_model.get_position(idx))

    def _calculate_max_distance(self):
        """Calculate maximum distance in the tree for normalization."""
        bounds = self.tree_model.bounds
        max_dist = 0
        for axis in range(3):
            max_dist += (bounds[axis][1] - bounds[axis][0]) ** 2
        return np.sqrt(max_dist)

    def update(self, dt: float):
        """Update sphere pulse animation."""
        self.clear()

        time = self.get_time()

        for pulse_idx, origin in enumerate(self.pulse_origins):
            # Each pulse has a phase offset
            phase = (pulse_idx / self.num_pulses)
            pulse_time = (time * self.speed + phase) % 1.0

            # Calculate pulse radius (0 to max)
            pulse_radius = pulse_time * self.max_distance

            # Calculate distances from origin for all LEDs
            distances = self.tree_model.get_distances_from_point(origin)

            # Light up LEDs near the pulse radius
            for i in range(self.led_count):
                dist_diff = abs(distances[i] - pulse_radius)
                dist_diff_norm = dist_diff / self.max_distance

                if dist_diff_norm < self.pulse_width:
                    brightness = 1.0 - (dist_diff_norm / self.pulse_width)
                    brightness = brightness ** 2

                    # Color based on pulse index
                    hue = phase
                    r, g, b = hsv_to_rgb(hue, 1.0, brightness)

                    # Add to existing color
                    current = self.pixels[i]
                    self.pixels[i] = np.minimum(
                        current + np.array([r, g, b]),
                        255
                    ).astype(np.uint8)
