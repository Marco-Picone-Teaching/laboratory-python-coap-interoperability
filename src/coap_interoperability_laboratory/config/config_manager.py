from pathlib import Path
from typing import Any

import yaml


class ConfigManager:
    """
    ConfigManager class loads the configuration shared by the laboratory scripts
    (the bind address of the CoAP server, the name of the device and the target server of the CoAP clients) from a YAML file.

    By default, the file `config.yaml` is searched in the current working directory and,
    if not found, in the project root directory.
    """

    # Default name of the configuration file
    DEFAULT_CONFIG_FILE_NAME = "config.yaml"

    # Project root directory: src/coap_interoperability_laboratory/config/config_manager.py -> 3 levels up
    PROJECT_ROOT_DIR = Path(__file__).resolve().parents[3]

    # Default values used when a parameter is not defined in the configuration file
    DEFAULT_SERVER_BIND_HOST = "127.0.0.1"
    DEFAULT_SERVER_PORT = 5683
    DEFAULT_CLIENT_SERVER_HOST = "127.0.0.1"
    DEFAULT_CLIENT_SERVER_PORT = 5683
    DEFAULT_DEVICE_NAME = "urn:dev:coffee-machine-0001:"

    def __init__(self, config_file_path: str | Path | None = None) -> None:
        """
        Constructor for ConfigManager class
        :param config_file_path: Path of the YAML configuration file. If None the default file is used
        """

        if config_file_path is None:
            config_file_path = self._find_default_config_file()

        self.config_file_path: Path = Path(config_file_path)

        # Load the configuration file into a Python dictionary
        with open(self.config_file_path, "r", encoding="utf-8") as config_file:
            self._config: dict[str, Any] = yaml.safe_load(config_file) or {}

    @classmethod
    def _find_default_config_file(cls) -> Path:
        """ Search the default configuration file in the current working directory and in the project root """

        candidate_paths = [Path.cwd() / cls.DEFAULT_CONFIG_FILE_NAME,
                           cls.PROJECT_ROOT_DIR / cls.DEFAULT_CONFIG_FILE_NAME]

        for candidate_path in candidate_paths:
            if candidate_path.is_file():
                return candidate_path

        raise FileNotFoundError(f"Configuration file not found. Searched in: {[str(p) for p in candidate_paths]}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Read a configuration value using a dotted key (e.g., "server.port")
        :param key: Dotted path of the configuration parameter
        :param default: Value returned if the parameter is not defined
        :return: The configuration value or the default one
        """

        value: Any = self._config
        for key_part in key.split("."):
            if not isinstance(value, dict) or key_part not in value:
                return default
            value = value[key_part]

        return value

    @property
    def server_bind_host(self) -> str:
        """ Local IP address on which the CoAP servers listen """
        return str(self.get("server.bind_host", self.DEFAULT_SERVER_BIND_HOST))

    @property
    def server_port(self) -> int:
        """ UDP port on which the CoAP servers listen """
        return int(self.get("server.port", self.DEFAULT_SERVER_PORT))

    @property
    def device_name(self) -> str:
        """ Name of the Coffee Machine, used as SenML Base Name (bn) by all the resources """
        return str(self.get("device.name", self.DEFAULT_DEVICE_NAME))

    @property
    def client_server_host(self) -> str:
        """ Host (IP address or hostname) of the CoAP Server targeted by the clients """
        return str(self.get("client.server_host", self.DEFAULT_CLIENT_SERVER_HOST))

    @property
    def client_server_port(self) -> int:
        """ UDP port of the CoAP Server targeted by the clients """
        return int(self.get("client.server_port", self.DEFAULT_CLIENT_SERVER_PORT))

    def build_server_uri(self, path: str) -> str:
        """
        Build the CoAP URI of a resource of the target server (e.g., coap://127.0.0.1:5683/temperature)
        :param path: Path of the resource (e.g., "temperature" or "/.well-known/core")
        :return: The complete CoAP URI of the resource
        """
        return f"coap://{self.client_server_host}:{self.client_server_port}/{path.lstrip('/')}"
