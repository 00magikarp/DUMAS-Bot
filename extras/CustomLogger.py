import logging
import os
from logging.handlers import TimedRotatingFileHandler


class CustomLogger:
    """
    Fields to pass into the :func:`log` function.

    Options for the mode are:

    - :attr:`INFO`
    - :attr:`WARNING`
    - :attr:`DEBUG`
    """
    INFO = logging.INFO
    WARNING = logging.WARNING
    DEBUG = logging.DEBUG

    def __init__(self, level: int):
        self.logger = logging.getLogger('discord')
        self.logger.setLevel(level)

        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(name)s: %(message)s')

        if not os.path.exists("log"):
            os.makedirs("log")

        handler = TimedRotatingFileHandler("log/discord.log", encoding='utf-8', when="midnight", interval=1, backupCount=14)
        handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.addHandler(console_handler)

    def log(self, text: str, logger_mode: int) -> None:
        """
        \"Custom\" Logger

        Prints to console and outputs to logger

        :param text: The text to be logged
        :param logger_mode: The mode of logging
        """

        if logger_mode == CustomLogger.INFO:
            self.logger.info(text)
        elif logger_mode == CustomLogger.WARNING:
            self.logger.warning(text)
        elif logger_mode == CustomLogger.DEBUG:
            self.logger.debug(text)
        else:
            self.logger.warning(f"ATTEMPT TO LOG FAILED. DEFAULTED TO WARNING.")
            self.logger.warning(text)

        return
