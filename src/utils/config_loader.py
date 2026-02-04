import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_config(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise

def get_model_config() -> Dict[str, Any]:
    """Get model-specific configuration"""
    config = load_config()
    return config.get("model_config", {})

def get_api_config() -> Dict[str, Any]:
    """Get API-specific configuration"""
    config = load_config()
    return config.get("api", {})

def get_data_config() -> Dict[str, Any]:
    """Get data processing configuration"""
    config = load_config()
    return config.get("data", {})