import os
import yaml
from pathlib import Path
from typing import Dict, Any
from ..utils.audio_utils import find_audio_devices, test_audio_devices
from .logger import get_logger

logger = get_logger(__name__)

class Config:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}
        self.load_config()
        self._setup_audio_devices()

    def load_config(self) -> None:
        """Load configuration from YAML files"""
        default_config_path = self.config_dir / "default_config.yaml"
        
        if not default_config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {default_config_path}")

        with open(default_config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Override with environment variables
        self._override_from_env()
        
    def _setup_audio_devices(self) -> None:
        """Setup audio devices automatically"""
        logger.info("Detecting audio devices...")
        output_device, input_device = find_audio_devices()
        
        if output_device and input_device:
            # Update config
            self.config.setdefault('audio', {})
            self.config['audio']['output_device'] = output_device
            self.config['audio']['input_device'] = input_device
            
            # Test devices
            if test_audio_devices(output_device, input_device):
                logger.info("Audio devices configured successfully")
                
                # Update environment variables
                os.environ['OUTPUT_DEVICE'] = output_device
                os.environ['INPUT_DEVICE_INDEX'] = str(input_device)
            else:
                logger.warning("Audio device tests failed, using default configuration")

    def _override_from_env(self) -> None:
        """Override configuration with environment variables"""
        env_mapping = {
            'OPENAI_API_KEY': ('ai', 'api_key'),
            'PORCUPINE_ACCESS_KEY': ('wake_word', 'access_key'),
            'INPUT_DEVICE_INDEX': ('audio', 'input_device'),
            'OUTPUT_DEVICE': ('audio', 'output_device'),
        }

        for env_var, config_path in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert to int for input device if necessary
                if env_var == 'INPUT_DEVICE_INDEX':
                    try:
                        value = int(value)
                    except ValueError:
                        logger.warning(f"Invalid input device index: {value}")
                        continue
                self._set_nested_value(self.config, config_path, value)

    def _set_nested_value(self, d: dict, path: tuple, value: Any) -> None:
        """Set a value in a nested dictionary using a path tuple"""
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value

    def get(self, *keys: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation"""
        value = self.config
        for key in keys:
            if not isinstance(value, dict):
                return default
            value = value.get(key, default)
            if value is None:
                return default
        return value

    def __getitem__(self, key: str) -> Any:
        """Get a top-level configuration value"""
        return self.config[key]

    def __contains__(self, key: str) -> bool:
        """Check if a top-level configuration key exists"""
        return key in self.config 