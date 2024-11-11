import os
import pytz
import inspect
import logging
from datetime import datetime
from colorama import init, Fore


# 初始化 colorama
init(autoreset=True)

china_tz = pytz.timezone('Asia/Shanghai')  # 时区

class CustomLogger:
    def __init__(self):
        self.console_logger = logging.getLogger("console_logger")
        self.console_logger.setLevel(logging.DEBUG)
        self.file_logger = logging.getLogger("file_logger")
        self.file_logger.setLevel(logging.DEBUG)
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(logging.Formatter('%(message)s'))
        self.console_logger.addHandler(self.console_handler)

    def set_log_level(self, level):
        level = level.upper()
        if level == 'DEBUG':
            self.console_logger.setLevel(logging.DEBUG)
            self.file_logger.setLevel(logging.DEBUG)
        elif level == 'INFO':
            self.console_logger.setLevel(logging.INFO)
            self.file_logger.setLevel(logging.INFO)
        elif level == 'WARNING':
            self.console_logger.setLevel(logging.WARNING)
            self.file_logger.setLevel(logging.WARNING)
        elif level == 'ERROR':
            self.console_logger.setLevel(logging.ERROR)
            self.file_logger.setLevel(logging.ERROR)
        self.console_handler.setLevel(level)

    def _log(self, level, message):
        caller_frame = inspect.stack()[3]
        frame = caller_frame[0]
        info = inspect.getframeinfo(frame)

        timestamp = datetime.now(china_tz).strftime("%Y-%m-%d %H:%M:%S")
        file_name = os.path.splitext(os.path.basename(info.filename))[0]
        line_number = info.lineno
        log_level = level.upper()
        try:
            message = repr(message)
        except Exception as e:
            message = f"<Failed to convert message to string: {e}>"

        log_message = f"[{timestamp}] <{log_level}> {file_name}:{line_number} - {message}"
        if level == 'info':
            self.console_logger.info(Fore.GREEN + log_message)
        elif level == 'debug':
            self.console_logger.debug(Fore.BLUE + log_message)
        elif level == 'error':
            self.console_logger.error(Fore.RED + log_message)
        elif level == 'warning':
            self.console_logger.warning(Fore.YELLOW + log_message)
        log_filename = datetime.now(china_tz).strftime("%Y_%m_%d-") + file_name + '.log'
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_filename)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        file_handler.setLevel(self.file_logger.level)
        self.file_logger.addHandler(file_handler)
        if level == 'info':
            self.file_logger.info(log_message)
        elif level == 'debug':
            self.file_logger.debug(log_message)
        elif level == 'error':
            self.file_logger.error(log_message)
        elif level == 'warning':
            self.file_logger.warning(log_message)
        self.file_logger.removeHandler(file_handler)
        file_handler.close()

    def info(self, message):
        self._log('info', message)

    def debug(self, message):
        self._log('debug', message)

    def error(self, message):
        self._log('error', message)

    def warning(self, message):
        self._log('warning', message)

logger = CustomLogger()

def set_log_level(level):
    logger.set_log_level(level)

def log_info(message):
    logger.info(message)

def log_debug(message):
    logger.debug(message)

def log_error(message):
    logger.error(message)

def log_warning(message):
    logger.warning(message)
