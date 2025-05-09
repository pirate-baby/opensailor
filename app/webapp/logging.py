from logging import getLogger, INFO, StreamHandler, Logger
import sys

logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler(sys.stdout))


def get_logger(name: str) -> "Logger":
    return getLogger(name)
