# WLED Christmas Tree Controller

A Python-based controller for creating custom 3D-aware LED effects for Christmas trees with addressable LEDs controlled by WLED on ESP32.

## Features

- **3D Spatial Awareness**: Uses X, Y, Z coordinates to create effects that work naturally with your tree's shape
- **WLED Integration**: Seamless communication with WLED via HTTP API and UDP (DDP) streaming
- **Extensible Effect System**: Easy-to-use base classes for creating custom effects
- **Pre-built Effects**: Multiple ready-to-use effects including:
  - Height Gradient - Color gradients based on tree height
  - Rising Wave - Waves traveling up the tree
  - Spiral - Spiraling patterns around the tree
  - Sphere Pulse - Expanding spheres of light
  - Rotating Plane - Planes of light rotating through the tree
  - Rainbow - Classic rainbow cycling effect
- **Configurable**: YAML-based configuration for easy customization
- **Real-time Streaming**: High-performance UDP streaming for smooth animations

## Requirements

- Python 3.8+
- WLED installed on ESP32 device
- WS2811/WS2812 addressable LEDs
- CSV file with X, Y, Z coordinates for each LED

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Update configuration file `config/config.yaml`:
   - Set your WLED device IP address
   - Adjust LED count if different from 1610
   - Configure FPS and other settings

4. Create or place your LED coordinate CSV file in `config/tree_coordinates.csv`

### CSV File Format

Your coordinate CSV should have one row per LED with X, Y, Z coordinates:

```csv
X,Y,Z
0.0,0.0,0.0
0.1,0.05,0.02
0.15,0.08,0.04
...
```

- Row order corresponds to LED index (0, 1, 2, ...)
- Header row is optional
- Units don't matter (will be normalized automatically)
- Can be generated from LED mapping tools or manually created

## Quick Start

### Run a built-in effect:

```bash
python main.py --coords config/tree_coordinates.csv --effect height_gradient
```

### Available command-line options:

```bash
python main.py --help

Options:
  --config PATH       Path to configuration file (default: config/config.yaml)
  --coords PATH       Path to CSV file with LED coordinates
  --effect NAME       Effect to run (default: height_gradient)
  --duration SECONDS  Duration in seconds (omit for infinite)
  --log-level LEVEL   Logging level (DEBUG, INFO, WARNING, ERROR)
```

### Available effects:

- `height_gradient` - Animated color gradient based on height
- `rising_wave` - Wave effect rising up the tree
- `spiral` - Spiral pattern around the tree
- `sphere_pulse` - Pulsing spheres emanating from points
- `rotating_plane` - Rotating plane of light
- `rainbow` - Classic rainbow cycle (doesn't require coordinates)

## Creating Custom Effects

### Simple custom effect:

```python
from src.effect_base import Effect
from src.tree_model import TreeModel
from utils.color_utils import hsv_to_rgb

class MyEffect(Effect):
    def __init__(self, led_count, fps=30, tree_model=None, **kwargs):
        super().__init__(led_count, fps, tree_model, **kwargs)
        # Your initialization here

    def update(self, dt):
        """Called every frame - implement your effect logic here."""
        time = self.get_time()

        for i in range(self.led_count):
            # Get LED position if using tree model
            if self.tree_model:
                pos = self.tree_model.get_position(i)
                height = self.tree_model.get_height_normalized()[i]

            # Calculate color based on your logic
            hue = (height + time * 0.1) % 1.0
            r, g, b = hsv_to_rgb(hue, 1.0, 1.0)

            # Set pixel color
            self.set_pixel(i, r, g, b)
```

See `examples/create_custom_effect.py` for a complete example.

## Project Structure

```
tree/
├── config/
│   ├── config.yaml              # Main configuration file
│   └── tree_coordinates.csv     # LED position coordinates (you create this)
├── src/
│   ├── config_manager.py        # Configuration management
│   ├── wled_client.py           # WLED communication
│   ├── effect_base.py           # Base effect class
│   └── tree_model.py            # 3D coordinate management
├── effects/
│   ├── height_gradient.py       # Height-based gradient effect
│   ├── rising_wave.py           # Rising wave effect
│   ├── spiral.py                # Spiral effect
│   ├── sphere_pulse.py          # Pulsing sphere effect
│   ├── rotating_plane.py        # Rotating plane effect
│   └── rainbow.py               # Rainbow effect
├── utils/
│   ├── color_utils.py           # Color conversion utilities
│   └── spatial_utils.py         # 3D spatial utilities
├── examples/
│   ├── simple_effect.py         # Simple usage example
│   └── create_custom_effect.py  # Custom effect example
├── main.py                      # Main application
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Configuration

Edit `config/config.yaml` to customize settings:

```yaml
wled:
  host: "192.168.1.100"  # Your WLED IP address
  http_port: 80
  ws_port: 81
  use_udp: true
  udp_port: 4048

leds:
  count: 1610            # Number of LEDs
  fps: 30                # Target frame rate
  brightness: 128        # Default brightness (0-255)

effects:
  smooth_transitions: true
  transition_duration: 1.0
  auto_cycle: false
  auto_cycle_interval: 30

logging:
  level: "INFO"
```

## Effect Base Class API

The `Effect` base class provides these useful methods:

### Properties:
- `self.led_count` - Number of LEDs
- `self.fps` - Target frames per second
- `self.tree_model` - 3D tree model (if provided)
- `self.pixels` - Current pixel buffer (numpy array)

### Methods you implement:
- `update(dt)` - Called every frame, implement your effect logic here

### Methods you can use:
- `get_time()` - Get elapsed time since effect started
- `get_progress(duration)` - Get progress through a duration (0-1, wraps)
- `set_pixel(index, r, g, b)` - Set a single pixel color
- `set_all_pixels(r, g, b)` - Set all pixels to same color
- `clear()` - Clear all pixels (set to black)
- `fade_to_black(amount)` - Fade all pixels toward black
- `blur(amount)` - Apply blur effect

## TreeModel API

The `TreeModel` class provides spatial queries:

- `get_coordinates()` - Get all LED coordinates
- `get_position(led_index)` - Get position of specific LED
- `get_height_normalized()` - Get normalized heights (0=bottom, 1=top)
- `get_angle_from_center()` - Get angles around center axis
- `get_radial_distance()` - Get distance from center axis
- `get_distances_from_point(point)` - Get distances from all LEDs to a point
- `get_nearest_leds(point, count)` - Find nearest LEDs to a point
- `get_leds_in_sphere(center, radius)` - Get LEDs within a sphere
- `get_leds_in_range(axis, min, max)` - Get LEDs within axis range

## Utility Functions

### Color utilities (`utils.color_utils`):
- `hsv_to_rgb(h, s, v)` - Convert HSV to RGB
- `wheel(pos)` - Generate rainbow colors
- `blend_colors(color1, color2, ratio)` - Blend two colors
- `dim(color, factor)` - Dim a color
- `kelvin_to_rgb(kelvin)` - Color temperature to RGB

### Spatial utilities (`utils.spatial_utils`):
- `distance_3d(p1, p2)` - 3D distance calculation
- `normalize_vector(v)` - Normalize a vector
- `rotate_point_around_axis(point, axis, angle)` - 3D rotation
- `find_nearest_neighbors(coords, index, k)` - Find nearest neighbors

## Troubleshooting

### Effect not displaying:
1. Check WLED device is powered on and accessible
2. Verify IP address in config.yaml is correct
3. Ensure WLED is not running another effect
4. Check that realtime mode is enabled (should happen automatically)

### Coordinates not working correctly:
1. Verify CSV file has correct number of rows (one per LED)
2. Check CSV format (X,Y,Z columns)
3. Ensure CSV is saved in correct location
4. Look at logs for coordinate loading messages

### Performance issues:
1. Lower FPS in config.yaml
2. Reduce LED count if testing
3. Simplify effect calculations in update() method
4. Use UDP streaming (should be enabled by default)

## Tips for Creating Effects

1. **Start simple**: Begin with solid colors or simple patterns
2. **Use time wisely**: `self.get_time()` provides smooth animation timing
3. **Leverage spatial data**: Use TreeModel methods to create 3D-aware effects
4. **Test incrementally**: Test each part of your effect logic separately
5. **Normalize values**: Use 0-1 ranges for easier math
6. **Pre-calculate when possible**: Cache values that don't change per frame
7. **Use numpy**: Vectorized operations are much faster than loops

## Examples

See the `examples/` directory for:
- `simple_effect.py` - Basic example of running an effect
- `create_custom_effect.py` - Complete custom effect implementation

## License

This project is provided as-is for personal and educational use.

## Contributing

Feel free to create your own effects and share them! The modular design makes it easy to add new effects to the `effects/` directory.

## Acknowledgments

- Built for WLED firmware: https://github.com/Aircoookie/WLED
- Uses DDP (Distributed Display Protocol) for efficient LED streaming
