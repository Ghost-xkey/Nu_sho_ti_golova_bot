from airogram import Router

admin_router = Router()

@admin_router.message(Command('admin'))
async def admin_command(message: types.Message):
    await message.answer("Привет, админ!")
