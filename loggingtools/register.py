import logging

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")

levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}


class Logger:
    def __init__(self, level):
        self._logger = logging.getLogger("Logger")
        self._set_level(level)

    def _set_level(self, level):
        self._logger.setLevel(levels[level])

    def debug(self, place=None, message=None):
        self._logger.debug(f"{place} - {message}")

    def info(self, place=None, message=None):
        self._logger.info(f"{place} - {message}")

    def warning(self, place=None, message=None):
        self._logger.warning(f"{place} - {message}")

    def error(self, place=None, message=None):
        self._logger.error(f"{place} - {message}")

    def critical(self, place=None, message=None):
        self._logger.critical(f"{place} - {message}")
