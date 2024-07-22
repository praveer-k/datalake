import inspect
import logging
from enum import Enum
from datetime import datetime

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    @property
    def alias(self):
        if self.value == "warning":
            return "WARN"
        return self.value.upper()

class ColorFormatter(logging.Formatter):
    """Logging colored formatter"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    green = '\x1b[38;5;46m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

class FileNameFilter(logging.Filter):
    def filter(self, record):
        caller_frame = inspect.stack()[8]
        caller_module = inspect.getmodule(caller_frame[0])
        if caller_module is not None:
            module_dot_path = caller_module.__name__
            record.filename = module_dot_path
        else:
            record.filename = __name__
        return True
    
class Logger(logging.Logger):
    def __init__(self, stdout=True, file=True, level=logging.NOTSET):
        super().__init__("", level)
        self._setup_handlers(stdout, file)

    def _setup_handlers(self, stdout, file):
        fmt = '%(asctime)s | %(levelname)8s| %(message)s'
        color_formatter = ColorFormatter(fmt)
        file_name_filter = FileNameFilter() 
        # std out handler
        if stdout:
            stdout_handler = logging.StreamHandler()
            stdout_handler.setLevel(logging.DEBUG)
            stdout_handler.setFormatter(color_formatter)
            stdout_handler.addFilter(file_name_filter)
            self.addHandler(stdout_handler)
        # file handler
        if file:
            today = datetime.now()
            log_file_name = f'{self.name}_{today.strftime("%Y_%m_%d")}.log'
            file_handler = logging.FileHandler(log_file_name)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S'))
            file_handler.addFilter(file_name_filter)
            self.addHandler(file_handler)

