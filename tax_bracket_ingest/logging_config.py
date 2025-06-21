# tax_bracket_ingest/logging_config.py
import os
import logging
from logging.config import dictConfig
from pythonjsonlogger import jsonlogger

def setup_logging():
    env = os.getenv("ENV", "dev").lower()
    level =  logging.DEBUG if env == "dev" else logging.INFO
    
    log_path = os.getenv("LOG_PATH", "logs/tax_bracket_ingest.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    retention  = int(os.getenv("LOG_RETENTION_DAYS", 7))
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": jsonlogger.JsonFormatter,
                "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s"
            }
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": log_path,
                "when": "D",
                "backupCount": retention,
                "formatter": "json",
                "encoding": "utf-8",
                "interval": 1,
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "level": level,
            "handlers": ["file", "console"]
        }
    }

    dictConfig(logging_config)