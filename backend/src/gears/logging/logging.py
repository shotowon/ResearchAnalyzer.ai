from typing import Literal
import logging.config
import atexit

import json
from logging.handlers import QueueHandler
from pathlib import Path


def setup_logger(env: Literal["local", "dev", "prod"]) -> None:
    log_cfg_path = Path(__file__).parent.absolute() / "configs" / f"{env}.json"

    with open(log_cfg_path, "r") as f:
        logging.config.dictConfig(json.load(f))

    queue_handler: QueueHandler = logging.getHandlerByName("queue")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
