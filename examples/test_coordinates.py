"""Test script to validate coordinate CSV file and visualize the tree structure."""

import sys
import numpy as np
from src.tree_model import TreeModel


def test_coordinates(csv_path: str):
    """
    Test loading and display info about coordinate file.

    Args:
        csv_path: Path to CSV file
    """
    print(f"\nTesting coordinate file: {csv_path}")
    print("=" * 60)

    try:
        # Load tree model
        tree_model = TreeModel(csv_path=csv_path)

        print(f"\nSuccessfully loaded {tree_model.led_count} LED coordinates")

        # Display bounds
        print(f"\nTree Bounds:")
        print(f"  X: {tree_model.bounds[0][0]:.3f} to {tree_model.bounds[0][1]:.3f}")
        print(f"  Y: {tree_model.bounds[1][0]:.3f} to {tree_model.bounds[1][1]:.3f}")
        print(f"  Z: {tree_model.bounds[2][0]:.3f} to {tree_model.bounds[2][1]:.3f}")

        # Display center
        print(f"\nTree Center: [{tree_model.center[0]:.3f}, {tree_model.center[1]:.3f}, {tree_model.center[2]:.3f}]")

        # Display some sample positions
        print(f"\nSample LED Positions:")
        sample_indices = [0, tree_model.led_count // 4, tree_model.led_count // 2,
                         3 * tree_model.led_count // 4, tree_model.led_count - 1]

        for idx in sample_indices:
            if idx < tree_model.led_count:
                pos = tree_model.get_position(idx)
                height = tree_model.get_height_normalized()[idx]
                angle = tree_model.get_angle_from_center()[idx]
                radial = tree_model.get_radial_distance()[idx]

                print(f"  LED {idx:4d}: pos=[{pos[0]:6.3f}, {pos[1]:6.3f}, {pos[2]:6.3f}] "
                      f"height={height:.3f} angle={angle:.3f} radial={radial:.3f}")

        # Statistics
        heights = tree_model.get_height_normalized()
        radials = tree_model.get_radial_distance()
        angles = tree_model.get_angle_from_center()

        print(f"\nStatistics:")
        print(f"  Height - min: {np.min(heights):.3f}, max: {np.max(heights):.3f}, "
              f"mean: {np.mean(heights):.3f}")
        print(f"  Radial - min: {np.min(radials):.3f}, max: {np.max(radials):.3f}, "
              f"mean: {np.mean(radials):.3f}")
        print(f"  Angle  - min: {np.min(angles):.3f}, max: {np.max(angles):.3f}")

        # Check for duplicates
        unique_coords = np.unique(tree_model.coordinates, axis=0)
        if len(unique_coords) < tree_model.led_count:
            print(f"\nWARNING: Found {tree_model.led_count - len(unique_coords)} duplicate coordinates!")
        else:
            print(f"\nAll coordinates are unique ✓")

        print("\n" + "=" * 60)
        print("Coordinate file validation completed successfully!")

    except FileNotFoundError:
        print(f"\nERROR: File not found: {csv_path}")
        print("Please ensure the CSV file exists and the path is correct.")
    except Exception as e:
        print(f"\nERROR: Failed to load coordinates: {e}")


def generate_example_spiral(led_count: int, output_path: str):
    """
    Generate an example spiral coordinate pattern for testing.

    Args:
        led_count: Number of LEDs
        output_path: Output CSV file path
    """
    import csv

    print(f"\nGenerating example spiral with {led_count} LEDs...")

    coords = []
    height = 0
    angle = 0
    radius_start = 0.3
    radius_end = 0.05

    for i in range(led_count):
        t = i / led_count

        # Spiral parameters
        radius = radius_start * (1 - t) + radius_end * t
        angle = t * 10 * 2 * np.pi  # 10 rotations
        height = t

        # Convert to Cartesian
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = height

        coords.append([x, y, z])

    # Write to CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['X', 'Y', 'Z'])
        writer.writerows(coords)

    print(f"Generated {led_count} coordinates and saved to: {output_path}")
    print("You can use this file for testing effects!")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Test existing file:")
        print("    python test_coordinates.py path/to/coordinates.csv")
        print("\n  Generate example spiral:")
        print("    python test_coordinates.py --generate output.csv [led_count]")
        return

    if sys.argv[1] == '--generate':
        if len(sys.argv) < 3:
            print("ERROR: Please specify output file path")
            return

        output_path = sys.argv[2]
        led_count = int(sys.argv[3]) if len(sys.argv) > 3 else 1610

        generate_example_spiral(led_count, output_path)
        test_coordinates(output_path)
    else:
        test_coordinates(sys.argv[1])


if __name__ == '__main__':
    main()
