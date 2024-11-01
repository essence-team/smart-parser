import yaml
from core.config.models.database import DatabaseConfig
from core.config.models.loggers import LoggersConfig
from core.config.models.telethon import TelethonConfig
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    env: str
    access_api_key: str

    database: DatabaseConfig
    loggers: LoggersConfig
    telethon: TelethonConfig


def load_yaml_config(file_path: str):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def load_config() -> Config:
    load_dotenv(dotenv_path="/.env", verbose=True)

    yaml_config = load_yaml_config("core/config/config.yaml")

    database = DatabaseConfig()
    loggers = LoggersConfig()
    telethon = TelethonConfig()

    if yaml_config is not None:
        settings = Config(**yaml_config, database=database, loggers=loggers)
    else:
        settings = Config(database=database, loggers=loggers, telethon=telethon)

    return settings


main_config = load_config()
