from typing import override, Literal
from logging import Filter, LogRecord
import logging


class NoErrors(Filter):
    @override
    def filter(self, record: LogRecord) -> bool | LogRecord:
        return record.levelno < logging.WARNING


class Env(Filter):
    def __init__(self, env: Literal["local", "dev", "prod"]) -> None:
        self._env = env

    @override
    def filter(self, record: LogRecord) -> bool | LogRecord:
        record.env = self._env
        return True
