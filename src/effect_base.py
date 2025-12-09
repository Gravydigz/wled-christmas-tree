"""Base class for LED effects."""

import time
import logging
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.tree_model import TreeModel

logger = logging.getLogger(__name__)


class Effect(ABC):
    """Abstract base class for all LED effects."""

    def __init__(self, led_count: int, fps: int = 30, tree_model: Optional['TreeModel'] = None, **kwargs):
        """
        Initialize the effect.

        Args:
            led_count: Number of LEDs
            fps: Target frames per second
            tree_model: Optional 3D tree model for spatially-aware effects
            **kwargs: Additional effect-specific parameters
        """
        self.led_count = led_count
        self.fps = fps
        self.frame_time = 1.0 / fps

        # 3D tree model (optional)
        self.tree_model = tree_model

        # Time tracking
        self.start_time = None
        self.current_time = 0.0
        self.frame_count = 0

        # Pixel buffer
        self.pixels = np.zeros((led_count, 3), dtype=np.uint8)

        # Effect state
        self.running = False

        # Store additional parameters
        self.params = kwargs

        model_info = " (with 3D model)" if tree_model else ""
        logger.info(f"Effect {self.__class__.__name__} initialized with {led_count} LEDs at {fps} FPS{model_info}")

    @abstractmethod
    def update(self, dt: float):
        """
        Update effect state for the current frame.

        This method should be overridden by subclasses to implement the effect logic.

        Args:
            dt: Delta time since last update in seconds
        """
        pass

    def start(self):
        """Start the effect."""
        self.start_time = time.time()
        self.current_time = 0.0
        self.frame_count = 0
        self.running = True
        self.on_start()
        logger.info(f"Effect {self.__class__.__name__} started")

    def stop(self):
        """Stop the effect."""
        self.running = False
        self.on_stop()
        logger.info(f"Effect {self.__class__.__name__} stopped")

    def reset(self):
        """Reset effect to initial state."""
        self.pixels.fill(0)
        self.frame_count = 0
        self.current_time = 0.0

    def on_start(self):
        """Called when effect starts. Override for custom initialization."""
        pass

    def on_stop(self):
        """Called when effect stops. Override for custom cleanup."""
        pass

    def get_pixels(self) -> np.ndarray:
        """
        Get the current pixel buffer.

        Returns:
            NumPy array of shape (led_count, 3) with RGB values (0-255)
        """
        return self.pixels

    def set_pixel(self, index: int, r: int, g: int, b: int):
        """
        Set a single pixel color.

        Args:
            index: LED index
            r, g, b: RGB values (0-255)
        """
        if 0 <= index < self.led_count:
            self.pixels[index] = [r, g, b]

    def set_all_pixels(self, r: int, g: int, b: int):
        """
        Set all pixels to the same color.

        Args:
            r, g, b: RGB values (0-255)
        """
        self.pixels[:] = [r, g, b]

    def clear(self):
        """Clear all pixels (set to black)."""
        self.pixels.fill(0)

    def fade_to_black(self, fade_amount: float = 0.1):
        """
        Fade all pixels toward black.

        Args:
            fade_amount: Amount to fade (0-1, higher = faster fade)
        """
        self.pixels = (self.pixels * (1.0 - fade_amount)).astype(np.uint8)

    def blur(self, amount: float = 0.5):
        """
        Apply a simple blur effect.

        Args:
            amount: Blur amount (0-1)
        """
        if amount <= 0:
            return

        # Simple box blur with neighbors
        blurred = self.pixels.copy()
        for i in range(1, self.led_count - 1):
            blurred[i] = (
                self.pixels[i - 1] * 0.25 +
                self.pixels[i] * 0.5 +
                self.pixels[i + 1] * 0.25
            )
        self.pixels = (self.pixels * (1 - amount) + blurred * amount).astype(np.uint8)

    def get_time(self) -> float:
        """Get elapsed time since effect started."""
        return self.current_time

    def get_progress(self, duration: float) -> float:
        """
        Get progress through a duration (0-1, wraps).

        Args:
            duration: Duration in seconds

        Returns:
            Progress value (0-1)
        """
        return (self.current_time % duration) / duration

    def tick(self) -> np.ndarray:
        """
        Advance the effect by one frame.

        Returns:
            Current pixel buffer
        """
        if not self.running:
            return self.pixels

        # Calculate delta time
        if self.start_time is None:
            self.start_time = time.time()

        current = time.time()
        dt = current - (self.start_time + self.current_time)
        self.current_time += dt
        self.frame_count += 1

        # Update effect
        self.update(dt)

        return self.pixels

    def __repr__(self):
        return f"{self.__class__.__name__}(led_count={self.led_count}, fps={self.fps})"
