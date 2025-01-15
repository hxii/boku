from boku import __version__
from pathlib import Path
import os
from boku.logger import logger


class ConfigurationHandler:
    """Handle boku config file."""

    DEFAULT_CONFIG = f"""
    # Boku config - version {__version__}
    """

    _instance = None

    def __new__(cls) -> "ConfigurationHandler":
        """Singleton class."""
        if cls._instance is None:
            cls._instance = super(ConfigurationHandler, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self) -> None:
        """Initialize ConfigurationHandler."""
        self.config_dir = self.get_config_dir()
        self.global_task_dir = self.config_dir / "tasks"
        self.global_task_dir.mkdir(exist_ok=True)

    def get_config_dir(self) -> Path:
        """Get config directory for boku.

        Returns:
            (Path) path of the config directory.
        """
        if os.environ.get("BOKU_CONFIG_DIR"):
            config_dir = Path(os.environ.get("BOKU_CONFIG_DIR", "")).expanduser()
            logger.debug(f"Using BOKU_CONFIG_DIR env var: {config_dir}")
        else:
            if os.name == "nt":  # Windows
                base = os.environ.get("APPDATA") or os.path.expanduser(
                    "~\\AppData\\Roaming"
                )
            else:  # Unix-like systems (Linux, macOS)
                base = os.path.expanduser(
                    os.environ.get("XDG_CONFIG_HOME", "~/.config")
                )
            config_dir = Path(base) / "boku"
            logger.debug(f"Using default config dir: {config_dir}")

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def get_config_file(self) -> Path:
        """Return config file path."""
        config_path = self.config_dir / "config.yml"
        if not config_path.exists():
            self.default_config(config_path)
        return config_path

    def default_config(self, config_path: Path) -> str:
        """Write default configuration to file."""
        logger.debug(f"Config file {config_path} doesn't exist. Creating default.")
        config_path.touch()
        config_path.write_text(self.DEFAULT_CONFIG.strip())
        return ""
