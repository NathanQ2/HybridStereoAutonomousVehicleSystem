from colorama import Fore, Back, Style
from enum import Enum

# TODO: add record field / publish to visualizer


class LogLevel(Enum):
    NONE = 0  # Disables all logging
    RELEASE = 1  # Disables traces only
    DEBUG = 2  # Enables all log message
    # ALL = 3  # Prints all records

    @staticmethod
    def canTrace(logLevel) -> bool:
        return logLevel == LogLevel.DEBUG

    @staticmethod
    def canInfo(logLevel) -> bool:
        return logLevel != LogLevel.NONE

    @staticmethod
    def canWarn(logLevel) -> bool:
        return logLevel != LogLevel.NONE

    @staticmethod
    def canError(logLevel) -> bool:
        return logLevel != LogLevel.NONE


class Logger:
    COLOR_INFO = Fore.GREEN
    COLOR_WARN = Fore.YELLOW
    COLOR_ERROR = Fore.RED
    COLOR_RESET = Style.RESET_ALL

    def __init__(self, subsystem: str, logLevel: LogLevel = LogLevel.DEBUG):
        self.subsystem = subsystem
        self.logLevel = logLevel

    def assrt(self, condition: bool, message: str):
        assert condition, f"[ASSERT] {self.subsystem}: {message}"

    def trace(self, message: str, end='\n'):
        print(f"[TRACE] {self.subsystem}: {message}", end=end)

    def info(self, message: str, end='\n'):
        print(f"{self.COLOR_INFO}[INFO] {self.subsystem}: {message}{self.COLOR_RESET}", end=end)

    def warn(self, message: str, end='\n'):
        print(f"{self.COLOR_WARN}[WARN] {self.subsystem}: {message}{self.COLOR_RESET}", end=end)

    def error(self, message: str, end='\n'):
        print(f"{self.COLOR_ERROR}[ERROR] {self.subsystem}: {message}{self.COLOR_RESET}", end=end)
