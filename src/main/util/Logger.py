import time
from enum import Enum
from typing import Any, Self

from colorama import Fore, Style


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


class LogFrame:
    def __init__(self, startTime: float):
        self.values = {
            "timestamp": startTime
        }


class Logger:
    COLOR_INFO = Fore.GREEN
    COLOR_WARN = Fore.YELLOW
    COLOR_ERROR = Fore.RED
    COLOR_RESET = Style.RESET_ALL

    hasRootInit = False
    root = None

    def __init__(self, name: str, logLevel: LogLevel = LogLevel.DEBUG, parent: Self | None = None):
        self.name = name
        self.logPath = f"{parent.logPath}/{self.name}" if (parent is not None) else ""
        self.logLevel = logLevel
        self.parent = parent
        self.isRoot = False

        if (parent is None):
            assert Logger.hasRootInit == False, "Two root loggers have been initialized!"

            self.currentFrame: LogFrame = LogFrame(time.time())
            self.isRoot = True
            Logger.hasRootInit = True
            Logger.root = self

    def getChild(self, name: str, logLevel: LogLevel | None = None) -> Self:
        return Logger(
            name,
            logLevel if (logLevel is not None) else self.logLevel,
            self
        )

    def assrt(self, condition: bool, message: str):
        assert condition, f"[ASSERT] {self.name}: {message}"

    def trace(self, message: str, end='\n'):
        if (LogLevel.canTrace(self.logLevel)):
            print(f"[TRACE] {self.name}: {message}", end=end)

    def info(self, message: str, end='\n'):
        if (LogLevel.canInfo(self.logLevel)):
            print(f"{self.COLOR_INFO}[INFO] {self.name}: {message}{self.COLOR_RESET}", end=end)

    def warn(self, message: str, end='\n'):
        if (LogLevel.canWarn(self.logLevel)):
            print(f"{self.COLOR_WARN}[WARN] {self.name}: {message}{self.COLOR_RESET}", end=end)

    def error(self, message: str, end='\n'):
        if (LogLevel.canError(self.logLevel)):
            print(f"{self.COLOR_ERROR}[ERROR] {self.name}: {message}{self.COLOR_RESET}", end=end)

    def record(self, key: str, value: Any, allowTrace: bool = True):
        if (self.isRoot):
            self.currentFrame.values[key] = value
        else:
            Logger.root.record(f"{self.logPath}/{key}", value, allowTrace, )

            if (LogLevel.canTrace(self.logLevel) and allowTrace):
                print(f"[TRACE] {self.logPath}/{key}: {value}")

    def getRootFrame(self) -> LogFrame:
        if (self.isRoot):
            oldFrame = self.currentFrame
            self.currentFrame = LogFrame(time.time())
            return oldFrame
        else:
            return Logger.root.getRootFrame()
