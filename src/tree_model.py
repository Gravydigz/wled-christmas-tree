"""3D tree model for spatially-aware LED effects."""

import numpy as np
import csv
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


class TreeModel:
    """Manages 3D coordinate data for LED positions on the tree."""

    def __init__(self, csv_path: Optional[str] = None, led_count: int = 1610):
        """
        Initialize tree model.

        Args:
            csv_path: Path to CSV file with X,Y,Z coordinates
            led_count: Expected number of LEDs
        """
        self.led_count = led_count
        self.coordinates = None
        self.bounds = None
        self.center = None

        if csv_path:
            self.load_from_csv(csv_path)
        else:
            logger.warning("No CSV path provided, using linear mapping as fallback")
            self._create_linear_fallback()

    def load_from_csv(self, csv_path: str):
        """
        Load LED coordinates from CSV file.

        Expected CSV format:
        - Header row (optional): X,Y,Z or similar
        - Each row: x,y,z coordinates for one LED
        - Row order corresponds to LED index (0, 1, 2, ...)

        Args:
            csv_path: Path to CSV file
        """
        try:
            coordinates = []
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)

                # Try to detect and skip header
                first_row = next(reader)
                try:
                    # Try to parse first row as floats
                    coords = [float(x) for x in first_row]
                    coordinates.append(coords)
                except ValueError:
                    # First row is header, skip it
                    pass

                # Read remaining rows
                for row in reader:
                    if len(row) >= 3:
                        x, y, z = float(row[0]), float(row[1]), float(row[2])
                        coordinates.append([x, y, z])

            self.coordinates = np.array(coordinates, dtype=np.float32)

            if len(self.coordinates) != self.led_count:
                logger.warning(
                    f"CSV contains {len(self.coordinates)} coordinates "
                    f"but expected {self.led_count} LEDs"
                )
                self.led_count = len(self.coordinates)

            self._calculate_bounds()
            logger.info(f"Loaded {len(self.coordinates)} LED coordinates from {csv_path}")
            logger.info(f"Tree bounds: X[{self.bounds[0]}], Y[{self.bounds[1]}], Z[{self.bounds[2]}]")

        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_path}")
            self._create_linear_fallback()
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            self._create_linear_fallback()

    def _create_linear_fallback(self):
        """Create a simple linear fallback mapping if CSV not available."""
        logger.info("Creating linear fallback coordinates")
        # Simple vertical line for fallback
        self.coordinates = np.zeros((self.led_count, 3), dtype=np.float32)
        self.coordinates[:, 2] = np.linspace(0, 1, self.led_count)  # Z axis
        self._calculate_bounds()

    def _calculate_bounds(self):
        """Calculate bounding box and center of the tree."""
        if self.coordinates is None:
            return

        min_coords = np.min(self.coordinates, axis=0)
        max_coords = np.max(self.coordinates, axis=0)

        self.bounds = (
            (min_coords[0], max_coords[0]),  # X range
            (min_coords[1], max_coords[1]),  # Y range
            (min_coords[2], max_coords[2])   # Z range
        )

        self.center = np.mean(self.coordinates, axis=0)

    def get_coordinates(self) -> np.ndarray:
        """
        Get all LED coordinates.

        Returns:
            NumPy array of shape (led_count, 3) with X,Y,Z coordinates
        """
        return self.coordinates

    def get_position(self, led_index: int) -> np.ndarray:
        """
        Get position of a specific LED.

        Args:
            led_index: LED index

        Returns:
            NumPy array [x, y, z]
        """
        return self.coordinates[led_index]

    def get_distance(self, led_index: int, point: np.ndarray) -> float:
        """
        Calculate distance from LED to a point.

        Args:
            led_index: LED index
            point: 3D point [x, y, z]

        Returns:
            Euclidean distance
        """
        return np.linalg.norm(self.coordinates[led_index] - point)

    def get_distances_from_point(self, point: np.ndarray) -> np.ndarray:
        """
        Calculate distances from all LEDs to a point.

        Args:
            point: 3D point [x, y, z]

        Returns:
            NumPy array of distances for each LED
        """
        return np.linalg.norm(self.coordinates - point, axis=1)

    def get_nearest_leds(self, point: np.ndarray, count: int = 1) -> np.ndarray:
        """
        Find nearest LEDs to a point.

        Args:
            point: 3D point [x, y, z]
            count: Number of nearest LEDs to return

        Returns:
            Array of LED indices sorted by distance
        """
        distances = self.get_distances_from_point(point)
        return np.argsort(distances)[:count]

    def get_leds_in_sphere(self, center: np.ndarray, radius: float) -> np.ndarray:
        """
        Get all LEDs within a spherical region.

        Args:
            center: Center point [x, y, z]
            radius: Sphere radius

        Returns:
            Array of LED indices within the sphere
        """
        distances = self.get_distances_from_point(center)
        return np.where(distances <= radius)[0]

    def get_leds_in_range(self, axis: int, min_val: float, max_val: float) -> np.ndarray:
        """
        Get LEDs within a range along a specific axis.

        Args:
            axis: Axis index (0=X, 1=Y, 2=Z)
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Array of LED indices in range
        """
        coords = self.coordinates[:, axis]
        return np.where((coords >= min_val) & (coords <= max_val))[0]

    def normalize_coordinates(self) -> np.ndarray:
        """
        Get normalized coordinates (0-1 range for each axis).

        Returns:
            Normalized coordinates array
        """
        normalized = self.coordinates.copy()
        for axis in range(3):
            min_val, max_val = self.bounds[axis]
            if max_val > min_val:
                normalized[:, axis] = (normalized[:, axis] - min_val) / (max_val - min_val)
        return normalized

    def get_height_normalized(self) -> np.ndarray:
        """
        Get normalized height (Z-axis) for each LED (0=bottom, 1=top).

        Returns:
            Array of normalized heights
        """
        z_coords = self.coordinates[:, 2]
        z_min, z_max = self.bounds[2]
        if z_max > z_min:
            return (z_coords - z_min) / (z_max - z_min)
        return np.zeros(self.led_count)

    def get_angle_from_center(self) -> np.ndarray:
        """
        Get angle around Z-axis from center for each LED (in radians).

        Returns:
            Array of angles (0 to 2*pi)
        """
        # Calculate angle from center in XY plane
        centered = self.coordinates[:, :2] - self.center[:2]
        angles = np.arctan2(centered[:, 1], centered[:, 0])
        # Convert to 0-2pi range
        angles = (angles + 2 * np.pi) % (2 * np.pi)
        return angles

    def get_radial_distance(self) -> np.ndarray:
        """
        Get radial distance from center axis (Z-axis) for each LED.

        Returns:
            Array of radial distances
        """
        centered = self.coordinates[:, :2] - self.center[:2]
        return np.linalg.norm(centered, axis=1)

    def __repr__(self):
        return f"TreeModel(led_count={self.led_count}, bounds={self.bounds})"
