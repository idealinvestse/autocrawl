import logging
import sys
import asyncio

class Logger:
    def __init__(self, level):
        self.logger = logging.getLogger(__name__)
        level = getattr(logging, level.upper(), logging.INFO)  # Default to INFO level if not found.
        self.logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def log(self, message):
        # Log messages can be handled synchronously since they are not I/O bound.
        # However, keeping it async for consistency with the error method.
        self.logger.info(message)

    async def error(self, message):
        # Error messages can be handled synchronously since they are not I/O bound.
        # However, keeping it async for consistency with the log method.
        self.logger.error(message)