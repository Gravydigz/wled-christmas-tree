"""Color utility functions for LED effects."""

import numpy as np
import colorsys
from typing import Tuple


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """
    Convert HSV to RGB.

    Args:
        h: Hue (0-1)
        s: Saturation (0-1)
        v: Value/Brightness (0-1)

    Returns:
        RGB tuple (0-255, 0-255, 0-255)
    """
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def hsv_to_rgb_array(hsv_array: np.ndarray) -> np.ndarray:
    """
    Convert array of HSV values to RGB.

    Args:
        hsv_array: NumPy array of shape (n, 3) with HSV values (0-1)

    Returns:
        NumPy array of shape (n, 3) with RGB values (0-255)
    """
    rgb = np.zeros_like(hsv_array)
    for i in range(len(hsv_array)):
        rgb[i] = hsv_to_rgb(hsv_array[i, 0], hsv_array[i, 1], hsv_array[i, 2])
    return rgb.astype(np.uint8)


def wheel(pos: int) -> Tuple[int, int, int]:
    """
    Generate rainbow colors across 0-255 positions.

    Args:
        pos: Position in color wheel (0-255)

    Returns:
        RGB tuple
    """
    pos = 255 - pos
    if pos < 85:
        return (255 - pos * 3, 0, pos * 3)
    elif pos < 170:
        pos -= 85
        return (0, pos * 3, 255 - pos * 3)
    else:
        pos -= 170
        return (pos * 3, 255 - pos * 3, 0)


def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]:
    """
    Blend two colors.

    Args:
        color1: First RGB color
        color2: Second RGB color
        ratio: Blend ratio (0-1, 0 = all color1, 1 = all color2)

    Returns:
        Blended RGB color
    """
    ratio = max(0, min(1, ratio))
    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
    return (r, g, b)


def gamma_correct(color: np.ndarray, gamma: float = 2.2) -> np.ndarray:
    """
    Apply gamma correction to colors.

    Args:
        color: RGB array (0-255)
        gamma: Gamma value (default: 2.2)

    Returns:
        Gamma-corrected RGB array
    """
    return np.power(color / 255.0, gamma) * 255


def dim(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """
    Dim a color by a factor.

    Args:
        color: RGB color
        factor: Dimming factor (0-1)

    Returns:
        Dimmed RGB color
    """
    return (
        int(color[0] * factor),
        int(color[1] * factor),
        int(color[2] * factor)
    )


def random_color() -> Tuple[int, int, int]:
    """Generate a random RGB color."""
    return tuple(np.random.randint(0, 256, 3).tolist())


def kelvin_to_rgb(kelvin: float) -> Tuple[int, int, int]:
    """
    Convert color temperature in Kelvin to RGB.

    Args:
        kelvin: Color temperature (1000-40000K)

    Returns:
        RGB tuple
    """
    temp = kelvin / 100.0

    # Calculate red
    if temp <= 66:
        red = 255
    else:
        red = temp - 60
        red = 329.698727446 * (red ** -0.1332047592)
        red = max(0, min(255, red))

    # Calculate green
    if temp <= 66:
        green = temp
        green = 99.4708025861 * np.log(green) - 161.1195681661
    else:
        green = temp - 60
        green = 288.1221695283 * (green ** -0.0755148492)
    green = max(0, min(255, green))

    # Calculate blue
    if temp >= 66:
        blue = 255
    elif temp <= 19:
        blue = 0
    else:
        blue = temp - 10
        blue = 138.5177312231 * np.log(blue) - 305.0447927307
        blue = max(0, min(255, blue))

    return (int(red), int(green), int(blue))
