"""Main application for WLED Christmas Tree Controller."""

import time
import logging
import argparse
from src.config_manager import get_config
from src.wled_client import WLEDClient
from src.tree_model import TreeModel
from effects import *


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def run_effect(effect, wled_client, duration=None):
    """
    Run an effect for a specified duration.

    Args:
        effect: Effect instance to run
        wled_client: WLED client for streaming
        duration: Duration in seconds (None = run indefinitely)
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting effect: {effect.__class__.__name__}")

    # Enable WLED realtime mode
    wled_client.enable_realtime(timeout=255)

    # Start the effect
    effect.start()

    start_time = time.time()
    frame_count = 0

    try:
        while True:
            # Check duration
            if duration is not None and (time.time() - start_time) >= duration:
                break

            # Update effect
            pixels = effect.tick()

            # Stream to WLED
            wled_client.stream_pixels(pixels)

            frame_count += 1

            # Sleep to maintain target FPS
            elapsed = time.time() - start_time
            target_time = frame_count / effect.fps
            sleep_time = target_time - elapsed

            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        effect.stop()
        wled_client.disable_realtime()
        logger.info(f"Effect stopped after {frame_count} frames")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description='WLED Christmas Tree Controller')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--coords', type=str, help='Path to CSV file with LED coordinates')
    parser.add_argument('--effect', type=str, default='height_gradient',
                        help='Effect to run (height_gradient, rising_wave, spiral, sphere_pulse, rotating_plane, rainbow)')
    parser.add_argument('--duration', type=int, help='Duration in seconds (omit for infinite)')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level')

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Load configuration
    config = get_config(args.config)
    logger.info("Configuration loaded")

    # Load tree model
    tree_model = TreeModel(csv_path=args.coords, led_count=config.led_count)
    logger.info(f"Tree model loaded with {tree_model.led_count} LEDs")

    # Create WLED client
    wled_config = config.get_wled_config()
    wled_client = WLEDClient(
        host=wled_config['host'],
        http_port=wled_config.get('http_port', 80),
        udp_port=wled_config.get('udp_port', 4048)
    )
    logger.info(f"Connected to WLED at {wled_config['host']}")

    # Create effect
    effect_map = {
        'height_gradient': lambda: HeightGradientEffect(
            tree_model.led_count,
            fps=config.fps,
            tree_model=tree_model,
            animated=True
        ),
        'rising_wave': lambda: RisingWaveEffect(
            tree_model.led_count,
            fps=config.fps,
            tree_model=tree_model,
            speed=0.3
        ),
        'spiral': lambda: SpiralEffect(
            tree_model.led_count,
            fps=config.fps,
            tree_model=tree_model,
            speed=0.2
        ),
        'sphere_pulse': lambda: SpherePulseEffect(
            tree_model.led_count,
            fps=config.fps,
            tree_model=tree_model,
            speed=0.5
        ),
        'rotating_plane': lambda: RotatingPlaneEffect(
            tree_model.led_count,
            fps=config.fps,
            tree_model=tree_model,
            speed=0.3
        ),
        'rainbow': lambda: RainbowEffect(
            tree_model.led_count,
            fps=config.fps,
            speed=1.0
        )
    }

    if args.effect not in effect_map:
        logger.error(f"Unknown effect: {args.effect}")
        logger.info(f"Available effects: {', '.join(effect_map.keys())}")
        return

    effect = effect_map[args.effect]()

    # Run effect
    run_effect(effect, wled_client, duration=args.duration)

    # Cleanup
    wled_client.close()
    logger.info("Application terminated")


if __name__ == '__main__':
    main()
