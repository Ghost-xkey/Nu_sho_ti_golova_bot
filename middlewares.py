from aiogram import BaseMiddleware
import logging

class ExampleMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update, data):
        logging.info("Middleware activated")
        return data
