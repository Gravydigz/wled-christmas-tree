"""Spatial utility functions for 3D effects."""

import numpy as np
from typing import Tuple


def distance_3d(p1: np.ndarray, p2: np.ndarray) -> float:
    """
    Calculate Euclidean distance between two 3D points.

    Args:
        p1: First point [x, y, z]
        p2: Second point [x, y, z]

    Returns:
        Distance
    """
    return np.linalg.norm(p1 - p2)


def normalize_vector(v: np.ndarray) -> np.ndarray:
    """
    Normalize a vector to unit length.

    Args:
        v: Vector to normalize

    Returns:
        Normalized vector
    """
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm


def rotate_point_around_axis(point: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate a point around an axis using Rodrigues' rotation formula.

    Args:
        point: Point to rotate [x, y, z]
        axis: Rotation axis [x, y, z] (will be normalized)
        angle: Rotation angle in radians

    Returns:
        Rotated point
    """
    axis = normalize_vector(axis)
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)

    rotated = (point * cos_angle +
               np.cross(axis, point) * sin_angle +
               axis * np.dot(axis, point) * (1 - cos_angle))

    return rotated


def point_to_line_distance(point: np.ndarray, line_point: np.ndarray, line_direction: np.ndarray) -> float:
    """
    Calculate distance from a point to a line.

    Args:
        point: The point
        line_point: A point on the line
        line_direction: Direction vector of the line

    Returns:
        Distance from point to line
    """
    line_direction = normalize_vector(line_direction)
    point_to_line = point - line_point
    projection = np.dot(point_to_line, line_direction) * line_direction
    perpendicular = point_to_line - projection
    return np.linalg.norm(perpendicular)


def spherical_to_cartesian(r: float, theta: float, phi: float) -> Tuple[float, float, float]:
    """
    Convert spherical coordinates to Cartesian.

    Args:
        r: Radius
        theta: Azimuthal angle (0 to 2π)
        phi: Polar angle (0 to π)

    Returns:
        Cartesian coordinates (x, y, z)
    """
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    return (x, y, z)


def cartesian_to_spherical(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """
    Convert Cartesian coordinates to spherical.

    Args:
        x, y, z: Cartesian coordinates

    Returns:
        Spherical coordinates (r, theta, phi)
    """
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arctan2(y, x)
    phi = np.arccos(z / r) if r > 0 else 0
    return (r, theta, phi)


def interpolate_3d(p1: np.ndarray, p2: np.ndarray, t: float) -> np.ndarray:
    """
    Linear interpolation between two 3D points.

    Args:
        p1: First point
        p2: Second point
        t: Interpolation factor (0-1)

    Returns:
        Interpolated point
    """
    return p1 + (p2 - p1) * t


def find_nearest_neighbors(coordinates: np.ndarray, index: int, k: int = 5) -> np.ndarray:
    """
    Find k nearest neighbors to a point.

    Args:
        coordinates: Array of all coordinates (n, 3)
        index: Index of point to find neighbors for
        k: Number of neighbors to find

    Returns:
        Array of neighbor indices
    """
    point = coordinates[index]
    distances = np.linalg.norm(coordinates - point, axis=1)
    # Exclude the point itself
    distances[index] = np.inf
    return np.argsort(distances)[:k]


def calculate_bounding_sphere(coordinates: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Calculate bounding sphere for a set of points.

    Args:
        coordinates: Array of coordinates (n, 3)

    Returns:
        Tuple of (center, radius)
    """
    center = np.mean(coordinates, axis=0)
    distances = np.linalg.norm(coordinates - center, axis=1)
    radius = np.max(distances)
    return (center, radius)
