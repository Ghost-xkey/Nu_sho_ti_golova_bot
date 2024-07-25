from airogram import BaseMiddleware

class ExampleMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update, data):
        print("Middleware activated")
