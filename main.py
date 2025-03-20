from asyncio import run
from logging import getLogger, basicConfig, INFO

from handlers import user_handlers
from config import TOKEN

from aiogram import Bot, Dispatcher


logger = getLogger(__name__)


async def main() -> None:

    basicConfig(level=INFO,
                format='%(filename)s:%(lineno)d #%(levelname)-8s '
                       '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Бот успешно запущен')
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(user_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


run(main())