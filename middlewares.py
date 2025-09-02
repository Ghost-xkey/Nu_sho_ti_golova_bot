from aiogram import BaseMiddleware
from aiogram.types import Message
import logging
from typing import Any, Awaitable, Callable, Dict

class ExampleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        logging.info("Middleware activated")
        return await handler(event, data)
