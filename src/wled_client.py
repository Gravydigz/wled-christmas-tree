"""WLED client for controlling and streaming to WLED devices."""

import socket
import struct
import time
import requests
import logging
from typing import List, Tuple, Optional
import numpy as np


logger = logging.getLogger(__name__)


class WLEDClient:
    """Client for communicating with WLED devices."""

    def __init__(self, host: str, http_port: int = 80, udp_port: int = 4048):
        """
        Initialize WLED client.

        Args:
            host: IP address or hostname of WLED device
            http_port: HTTP API port (default: 80)
            udp_port: UDP port for DDP streaming (default: 4048)
        """
        self.host = host
        self.http_port = http_port
        self.udp_port = udp_port
        self.base_url = f"http://{host}:{http_port}"

        # Create UDP socket for streaming
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        logger.info(f"WLED Client initialized for {host}")

    def _api_request(self, endpoint: str, method: str = 'GET', json_data: dict = None) -> Optional[dict]:
        """
        Make an API request to WLED.

        Args:
            endpoint: API endpoint (e.g., '/json/state')
            method: HTTP method
            json_data: JSON data for POST requests

        Returns:
            Response JSON or None on error
        """
        url = f"{self.base_url}{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url, timeout=5)
            elif method == 'POST':
                response = requests.post(url, json=json_data, timeout=5)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None

    def get_info(self) -> Optional[dict]:
        """Get device information."""
        return self._api_request('/json/info')

    def get_state(self) -> Optional[dict]:
        """Get current device state."""
        return self._api_request('/json/state')

    def set_power(self, on: bool) -> bool:
        """
        Turn WLED on or off.

        Args:
            on: True to turn on, False to turn off

        Returns:
            True if successful
        """
        data = {"on": on}
        result = self._api_request('/json/state', method='POST', json_data=data)
        return result is not None

    def set_brightness(self, brightness: int) -> bool:
        """
        Set brightness.

        Args:
            brightness: Brightness value (0-255)

        Returns:
            True if successful
        """
        brightness = max(0, min(255, brightness))
        data = {"bri": brightness}
        result = self._api_request('/json/state', method='POST', json_data=data)
        return result is not None

    def set_effect(self, effect_id: int) -> bool:
        """
        Set a built-in WLED effect.

        Args:
            effect_id: Effect ID number

        Returns:
            True if successful
        """
        data = {"seg": [{"fx": effect_id}]}
        result = self._api_request('/json/state', method='POST', json_data=data)
        return result is not None

    def set_color(self, r: int, g: int, b: int) -> bool:
        """
        Set solid color.

        Args:
            r, g, b: RGB values (0-255)

        Returns:
            True if successful
        """
        data = {"seg": [{"col": [[r, g, b]]}]}
        result = self._api_request('/json/state', method='POST', json_data=data)
        return result is not None

    def enable_realtime(self, timeout: int = 255) -> bool:
        """
        Enable realtime mode for UDP streaming.

        Args:
            timeout: Timeout in seconds (1-255, 255 = infinite)

        Returns:
            True if successful
        """
        data = {"lor": timeout}
        result = self._api_request('/json/state', method='POST', json_data=data)
        return result is not None

    def disable_realtime(self) -> bool:
        """
        Disable realtime mode.

        Returns:
            True if successful
        """
        data = {"lor": 0}
        result = self._api_request('/json/state', method='POST', json_data=data)
        return result is not None

    def stream_pixels_ddp(self, pixels: np.ndarray, start_channel: int = 0) -> bool:
        """
        Stream pixel data using DDP (Distributed Display Protocol).

        Args:
            pixels: NumPy array of shape (num_pixels, 3) with RGB values (0-255)
            start_channel: Starting channel number (default: 0)

        Returns:
            True if successful
        """
        try:
            # Ensure pixels is the right shape and type
            if len(pixels.shape) != 2 or pixels.shape[1] != 3:
                raise ValueError("Pixels must be shape (num_pixels, 3)")

            pixels = pixels.astype(np.uint8)
            num_pixels = pixels.shape[0]

            # DDP can send up to 1440 bytes per packet (480 pixels)
            # For larger displays, we need to send multiple packets
            max_pixels_per_packet = 480

            for offset in range(0, num_pixels, max_pixels_per_packet):
                end = min(offset + max_pixels_per_packet, num_pixels)
                chunk = pixels[offset:end]
                chunk_size = (end - offset) * 3

                # Build DDP header
                # Flags: 0x01 = push (last packet in frame)
                flags = 0x01 if end >= num_pixels else 0x00

                header = struct.pack(
                    '!BBHHL',
                    0x41,  # Flags: V=1 (version), T=0 (timecode not present), P=0/1, Q=0, S=0, R=0
                    flags,  # Push flag
                    0,     # Sequence number (not used)
                    1,     # Data type: 1 = RGB
                    start_channel + (offset * 3)  # Start channel
                )

                # Add data length
                header += struct.pack('!H', chunk_size)

                # Flatten pixel data
                data = chunk.flatten().tobytes()

                # Send packet
                packet = header + data
                self.udp_socket.sendto(packet, (self.host, self.udp_port))

            return True
        except Exception as e:
            logger.error(f"Failed to stream pixels via DDP: {e}")
            return False

    def stream_pixels(self, pixels: np.ndarray) -> bool:
        """
        Stream pixel data to WLED.

        This is a convenience method that calls stream_pixels_ddp.

        Args:
            pixels: NumPy array of shape (num_pixels, 3) with RGB values (0-255)

        Returns:
            True if successful
        """
        return self.stream_pixels_ddp(pixels)

    def close(self):
        """Close connections and cleanup."""
        self.udp_socket.close()
        logger.info("WLED Client closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
