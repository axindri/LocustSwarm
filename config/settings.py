import json
from logging import DEBUG, INFO, getLogger
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from models.config import Config

logger = getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, env_prefix="", extra="ignore"
    )

    debug: bool = Field(default=True)
    logger_format: tuple[str, str] = ("%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

    docker_base_url: str = Field(default="unix:///var/run/docker.sock")

    allow_parallel: bool = Field(default=False)
    active_tests_cleanup_timeout: int = Field(default=60)  # in sec

    min_port: int = Field(default=8080)
    max_port: int = Field(default=8090)

    tmp_path: str = Field(default="./tmp")
    config_path: str = Field(default="./config.json")

    host: str = Field(default="http://ip")
    port: int = Field(default=3000)

    @property
    def results_path(self):
        return f"{self.tmp_path}/results"

    @property
    def config(self) -> Config:
        config_path = Path(self.config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Projects config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.debug(f"Load config.json from {config_path}")
        return Config.model_validate(data)

    @property
    def log_level(self) -> int:
        return DEBUG if self.debug else INFO


settings = Settings()
