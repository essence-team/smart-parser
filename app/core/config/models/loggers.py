from pydantic_settings import BaseSettings


class LoggersConfig(BaseSettings):
    logstash_host: str
    logstash_port: int
