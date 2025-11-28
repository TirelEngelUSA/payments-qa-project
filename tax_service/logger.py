import logging
import sys
from pythonjsonlogger import jsonlogger


def get_logger():
    logger = logging.getLogger('payments-api')
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s %(payment_id)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger