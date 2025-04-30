import asyncio
import logging
from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker
from handlers.handler_user import router_user_handler
from handlers.handler_admin import router_admin_handler

from setings import dp, bot


bot.my_admins_list = []
dp.include_routers(router_admin_handler, router_user_handler)


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()
    # await drop_db()
    await create_db()


async def on_shutdown(bot):
    print("бот лег")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await create_db()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def start_bot():
    logging.basicConfig(level=logging.INFO)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await create_db()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

# async def start_bot():
#     logging.basicConfig(level=logging.INFO)
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("Exit")

        
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("Exit")
