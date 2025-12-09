"""Configuration management for WLED Christmas Tree Controller."""

import os
import yaml
from typing import Any, Dict


class ConfigManager:
    """Manages configuration loading and access."""

    def __init__(self, config_path: str = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the configuration file. If None, uses default.
        """
        if config_path is None:
            # Default to config/config.yaml in project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(project_root, 'config', 'config.yaml')

        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing configuration file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'wled.host')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_wled_config(self) -> Dict[str, Any]:
        """Get WLED-specific configuration."""
        return self.config.get('wled', {})

    def get_led_config(self) -> Dict[str, Any]:
        """Get LED-specific configuration."""
        return self.config.get('leds', {})

    def get_effect_config(self) -> Dict[str, Any]:
        """Get effect-specific configuration."""
        return self.config.get('effects', {})

    @property
    def led_count(self) -> int:
        """Get the number of LEDs."""
        return self.get('leds.count', 1610)

    @property
    def fps(self) -> int:
        """Get the target frames per second."""
        return self.get('leds.fps', 30)

    @property
    def wled_host(self) -> str:
        """Get the WLED device host."""
        return self.get('wled.host', 'localhost')


# Global configuration instance
_config_instance = None


def get_config(config_path: str = None) -> ConfigManager:
    """
    Get the global configuration instance.

    Args:
        config_path: Path to configuration file (only used on first call)

    Returns:
        ConfigManager instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(config_path)
    return _config_instance
