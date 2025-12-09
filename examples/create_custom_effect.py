"""Example of creating a custom effect from scratch."""

import numpy as np
from src.effect_base import Effect
from src.tree_model import TreeModel
from utils.color_utils import hsv_to_rgb


class MyCustomEffect(Effect):
    """
    Example custom effect: Pulsing colors based on distance from center.
    """

    def __init__(self, led_count: int, fps: int = 30, tree_model: TreeModel = None,
                 speed: float = 1.0, **kwargs):
        """
        Initialize custom effect.

        Args:
            led_count: Number of LEDs
            fps: Frames per second
            tree_model: 3D tree model
            speed: Animation speed
        """
        super().__init__(led_count, fps, tree_model, **kwargs)

        if tree_model is None:
            raise ValueError("This effect requires a tree_model")

        self.speed = speed

        # Pre-calculate radial distances for all LEDs
        self.radial_distances = tree_model.get_radial_distance()
        self.max_distance = np.max(self.radial_distances)

        # Normalize distances to 0-1
        if self.max_distance > 0:
            self.radial_distances_norm = self.radial_distances / self.max_distance
        else:
            self.radial_distances_norm = np.zeros(led_count)

    def update(self, dt: float):
        """Update the effect for this frame."""
        time = self.get_time()

        # Create a pulsing wave based on time
        pulse = np.sin(time * self.speed * 2 * np.pi)

        for i in range(self.led_count):
            # Calculate brightness based on radial distance and time
            distance_factor = self.radial_distances_norm[i]

            # Pulse outward from center
            brightness_factor = np.sin(distance_factor * np.pi * 2 - time * self.speed * 2)
            brightness = max(0, brightness_factor) * 0.5 + 0.5

            # Color rotates through hue based on distance
            hue = (distance_factor + time * 0.1) % 1.0

            r, g, b = hsv_to_rgb(hue, 1.0, brightness)
            self.set_pixel(i, r, g, b)


def main():
    """Example of using the custom effect."""
    import time
    import logging
    from src.config_manager import get_config
    from src.wled_client import WLEDClient

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Load configuration
    config = get_config()

    # Load tree model
    tree_model = TreeModel(csv_path="config/tree_coordinates.csv", led_count=config.led_count)

    # Create WLED client
    wled_client = WLEDClient(host=config.wled_host)
    wled_client.enable_realtime(timeout=255)

    # Create our custom effect
    effect = MyCustomEffect(
        led_count=config.led_count,
        fps=config.fps,
        tree_model=tree_model,
        speed=0.5
    )

    effect.start()

    logger.info("Running custom effect for 30 seconds...")

    try:
        start_time = time.time()
        frame_count = 0

        while (time.time() - start_time) < 30:
            pixels = effect.tick()
            wled_client.stream_pixels(pixels)

            frame_count += 1
            elapsed = time.time() - start_time
            target_time = frame_count / effect.fps
            sleep_time = target_time - elapsed

            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        logger.info("Interrupted")
    finally:
        effect.stop()
        wled_client.disable_realtime()
        wled_client.close()
        logger.info("Done!")


if __name__ == '__main__':
    main()
