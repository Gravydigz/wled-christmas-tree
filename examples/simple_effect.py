"""Simple example of creating and running a custom effect."""

import time
import logging
from src.config_manager import get_config
from src.wled_client import WLEDClient
from src.tree_model import TreeModel
from effects.height_gradient import HeightGradientEffect

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run a simple effect example."""

    # Load configuration
    config = get_config()

    # Update the config file with your WLED IP address before running!
    wled_host = config.wled_host
    led_count = config.led_count
    fps = config.fps

    logger.info(f"Connecting to WLED at {wled_host}")

    # Load tree model from CSV
    # Make sure to update the path to your CSV file!
    tree_model = TreeModel(csv_path="config/tree_coordinates.csv", led_count=led_count)

    # Create WLED client
    wled_client = WLEDClient(host=wled_host)

    # Enable realtime mode
    wled_client.enable_realtime(timeout=255)

    # Create an effect - gradient from blue to red
    effect = HeightGradientEffect(
        led_count=led_count,
        fps=fps,
        tree_model=tree_model,
        colors=[(0, 0, 255), (255, 0, 0)],  # Blue to Red
        animated=True,
        speed=0.5
    )

    # Start the effect
    effect.start()

    logger.info("Running effect for 60 seconds... (Press Ctrl+C to stop)")

    try:
        start_time = time.time()
        frame_count = 0

        while (time.time() - start_time) < 60:
            # Update effect
            pixels = effect.tick()

            # Stream to WLED
            wled_client.stream_pixels(pixels)

            frame_count += 1

            # Maintain FPS
            elapsed = time.time() - start_time
            target_time = frame_count / fps
            sleep_time = target_time - elapsed

            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        effect.stop()
        wled_client.disable_realtime()
        wled_client.close()
        logger.info("Done!")


if __name__ == '__main__':
    main()
