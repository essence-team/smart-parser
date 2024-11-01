import logging

from core.config import main_config
from core.config.models.loggers import LoggersConfig
from logstash_async.formatter import LogstashFormatter
from logstash_async.handler import SynchronousLogstashHandler


def setup_logger(loggers_config: LoggersConfig) -> logging.Logger:
    logger = logging.getLogger("parser")
    logger.setLevel(logging.DEBUG)

    # LogstashHandler
    logstash_handler = SynchronousLogstashHandler(
        host=loggers_config.logstash_host,
        port=loggers_config.logstash_port,
        database_path=None,
    )
    logstash_handler.setLevel(logging.INFO)
    logstash_formatter = LogstashFormatter(
        message_type="python-log",
        extra_prefix="extra",
        extra=dict(environment=loggers_config.logs_env, application="parser"),
    )
    logstash_handler.setFormatter(logstash_formatter)
    logger.addHandler(logstash_handler)

    return logger


main_logger = setup_logger(loggers_config=main_config.loggers)
