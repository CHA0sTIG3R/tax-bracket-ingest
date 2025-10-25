# tax_bracket_ingest/logging_config.py
import os
import logging
from logging.config import dictConfig
from pythonjsonlogger import jsonlogger

def setup_logging():
    env = os.getenv("ENV", "dev").lower()
    level =  logging.DEBUG if env == "dev" else logging.INFO
    
    # detect lambda environment
    in_lambda = os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None
    
    log_to_file = os.getenv("LOG_TO_FILE")
    if log_to_file is None:
        log_to_file = not in_lambda
    else:
        log_to_file = log_to_file.strip().lower() in {"1", "true", "t", "yes", "y", "on"}
    
    default_path = "logs/tax_bracket_ingest.log"
    log_path = os.getenv("LOG_PATH", default_path)
    if in_lambda:
        base = os.path.basename(log_path) or "tax_bracket_ingest.log"
        log_path = os.path.join("/tmp", "logs", base)
    
    retention  = int(os.getenv("LOG_RETENTION_DAYS", 7))
    
    root_logger = logging.getLogger()
    if getattr(root_logger, "_configured_by_app", False):
        root_logger.setLevel(level)
        return
    
    file_handler_config = None
    if log_to_file:
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            file_handler_config = {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": log_path,
                "when": "D",
                "backupCount": retention,
                "formatter": "json",
                "encoding": "utf-8",
                "interval": 1,
            }
        except OSError:
            file_handler_config = None
    
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout"
        }
    }
    handler_names = ["console"]
    
    if file_handler_config:
        handlers["file"] = file_handler_config
        handler_names.append("file")
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": jsonlogger.JsonFormatter,
                "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s"
            }
        },
        "handlers": handlers,
        "root": {
            "level": level,
            "handlers": handler_names
        }
    }

    dictConfig(logging_config)
    root_logger._configured_by_app = True