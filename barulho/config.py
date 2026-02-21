"""Configuration management."""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Mapping:
    """A MIDI note to audio file mapping."""

    note: int
    file_path: str
    volume: float = 0.5
    velocity_sensitive: bool = True


@dataclass
class Config:
    """Application configuration."""

    global_volume: float = 0.8
    mappings: list[Mapping] = field(default_factory=list)


DEFAULT_CONFIG_DIR = Path.home() / ".config" / "barulho"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.json"


def load_config(path: Path | None = None) -> tuple[Config, Path]:
    """
    Load config from file.

    Returns:
        Tuple of (config, path_used)
    """
    config_path = path or DEFAULT_CONFIG_PATH

    if not config_path.exists():
        return Config(), config_path

    try:
        with open(config_path) as f:
            data = json.load(f)

        mappings = [Mapping(**m) for m in data.get("mappings", [])]
        config = Config(
            global_volume=data.get("global_volume", 0.8),
            mappings=mappings,
        )
        return config, config_path
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error loading config: {e}")
        return Config(), config_path


def save_config(config: Config, path: Path | None = None) -> Path:
    """
    Save config to file.

    Returns:
        Path where config was saved
    """
    config_path = path or DEFAULT_CONFIG_PATH

    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "global_volume": config.global_volume,
        "mappings": [asdict(m) for m in config.mappings],
    }

    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)

    return config_path
