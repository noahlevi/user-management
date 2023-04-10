import os
import logging

from pydantic_yaml import YamlModel, YamlStrEnum

log = logging.getLogger(__name__)


class LogLevel(YamlStrEnum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class MongoModel(YamlModel):
    dsn: str


class AppModel(YamlModel):
    debug: bool
    log_level: LogLevel
    docs_url: str | None = None
    jwt_secret_key: str
    jwt_refresh_secret_key: str
    algorithm: str | None = "HS256"
    access_token_expire_mins: int
    refresh_token_expire_mins: int


class Settings(YamlModel):
    app: AppModel
    mongo: MongoModel


class ConfigNotSpecified(Exception):
    pass


def init_config() -> None:
    config_path = os.environ.get("CONFIG")
    if not config_path:
        raise ConfigNotSpecified("Config should be specified with env var CONFIG")

    Config.c = Settings.parse_file(config_path)

    assert Config.c is not None


class Config:
    c: Settings = None  # type: ignore

    def __new__(cls, *args, **kwargs):
        raise RuntimeError("%s should not be instantiated" % cls)


def is_debug() -> bool:
    return Config.c.app.debug


def get_jwt_secret_key() -> bool:
    return Config.c.app.debug
