import getpass
from logging import basicConfig, getLogger, INFO

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

USER_NAME = getpass.getuser()

basicConfig(level=INFO)
log = getLogger()

TOKEN = "5190279756:AAH2rA0hZdtIziHSKm3A3YtXIIPihN4GXQ0"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo_message(msg: types.Message):
    print(2)
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)
