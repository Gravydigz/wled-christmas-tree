# Getting Started

Follow these steps to set up and run your WLED Christmas Tree Controller.

## Next Steps:

### 1. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Update Configuration

Edit `config/config.yaml` with your WLED device IP address:

```yaml
wled:
  host: "192.168.1.100"  # Change this to your WLED IP address
```

You can find your WLED IP address by:
- Checking your router's connected devices
- Looking at the WLED device's display (if it has one)
- Using the WLED app to find the device

### 3. Add Your LED Coordinates CSV File

Place your CSV file with LED coordinates at `config/tree_coordinates.csv`

**CSV Format Requirements:**
- One row per LED with X, Y, Z coordinates
- Row order corresponds to LED index (0, 1, 2, ...)
- Header row is optional
- See `config/tree_coordinates_example.csv` for format example

Example CSV format:
```csv
X,Y,Z
0.0,0.0,0.0
0.1,0.0,0.05
0.05,0.087,0.1
...
```

**Don't have coordinates yet?** You can generate a test spiral pattern:
```bash
python examples/test_coordinates.py --generate config/tree_coordinates.csv 1610
```

### 4. Test Your Coordinates

Validate your coordinate file before running effects:

```bash
python examples/test_coordinates.py config/tree_coordinates.csv
```

This will show you:
- Number of LEDs loaded
- Tree bounds and center
- Sample LED positions
- Statistics about your coordinate data
- Any warnings about duplicate coordinates

### 5. Run Your First Effect

Run a built-in effect to test everything is working:

```bash
python main.py --coords config/tree_coordinates.csv --effect height_gradient
```

**Available effects:**
- `height_gradient` - Animated color gradient based on height
- `rising_wave` - Wave effect rising up the tree
- `spiral` - Spiral pattern around the tree
- `sphere_pulse` - Pulsing spheres emanating from points
- `rotating_plane` - Rotating plane of light
- `rainbow` - Classic rainbow cycle

**Additional options:**
```bash
# Run for specific duration (30 seconds)
python main.py --coords config/tree_coordinates.csv --effect spiral --duration 30

# Change log level for debugging
python main.py --coords config/tree_coordinates.csv --effect rising_wave --log-level DEBUG
```

## Creating Custom Effects

The system is designed to be easily extensible. Create custom effects by:

1. Inheriting from the `Effect` base class
2. Implementing the `update()` method
3. Using the tree model for spatial queries

See `examples/create_custom_effect.py` for a complete example.

## Troubleshooting

**Effect not displaying:**
- Check WLED device is powered on and network accessible
- Verify IP address in `config/config.yaml` is correct
- Ensure WLED is not running another effect
- Check firewall settings aren't blocking UDP port 4048

**Coordinate issues:**
- Verify CSV has correct number of rows (one per LED)
- Check CSV format matches example
- Run `test_coordinates.py` to validate the file
- Look at console logs for loading errors

**Performance issues:**
- Lower FPS in `config/config.yaml` (try 20-25)
- Simplify effect calculations
- Ensure UDP streaming is enabled (default)

## Need Help?

- Check the main README.md for detailed documentation
- Look at examples in the `examples/` directory
- Review effect implementations in `effects/` directory

Enjoy your animated Christmas tree! 🎄
