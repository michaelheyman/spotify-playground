import logging
from datetime import datetime

from flask.helpers import get_debug_flag
from pythonjsonlogger import jsonlogger

from spotify.settings import DevConfig
from spotify.settings import ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


def suppress_module_logging():
    """Suppress the logging messages from certain modules to prevent noisy logs"""
    modules = ["requests"]

    for module in modules:
        logging.getLogger(module).setLevel(logging.WARNING)


suppress_module_logging()

logging.getLogger().setLevel(CONFIG.LOGGING_LEVEL)
logger = logging.getLogger(__name__)
logger.setLevel(CONFIG.LOGGING_LEVEL)
logHandler = logging.StreamHandler()
formatter = CustomJsonFormatter("(timestamp) (filename) (level) (message)")
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
