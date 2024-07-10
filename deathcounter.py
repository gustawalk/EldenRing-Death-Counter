import sys
import os
from PyQt5 import *
import pynput
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time
import threading
import pyautogui as pyag
import numpy as np
import cv2
import os
import json

path = "C:/DeathCounter/"
filename = "config.json"
fullpath = f"{path}{filename}"

def read_json(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    return data

def append_json(filepath, entry):
    data = read_json(filepath)
    data.append(entry)
    with open(filepath, 'w') as file:
        json.dump(data, file)

def search_data_json(filepath):
    data = read_json(filepath)
    
    return data['deaths'], data['text_size'], data['text_color'], data['language']

def create_json():
    if os.path.exists(fullpath):
        return

    if not os.path.exists(path):
        os.makedirs(path)
    
    data = {
        'deaths': 0,
        'text_size': 45,
        'text_color': 0,
        'language': 'en'
    }
    
    with open(fullpath, 'w') as file:
        json.dump(data, file)

def update_json(filepath, count, size, color, language):
    data = {
        'deaths': int(count),
        'text_size': int(size),
        'text_color': int(color),
        'language': str(language)
    }
    
    with open(filepath, 'w') as file:
        json.dump(data, file)

def reset_json(filepath, language):
    data = {
        'deaths': 0,
        'text_size': 45,
        'text_color': 0,
        'language': str(language)
    }
    
    with open(filepath, 'w') as file:
        json.dump(data, file)

class MainWindow(QMainWindow):

    def __init__(self, aw=200, ah=30):
        super().__init__()

        self.aw = aw
        self.ah = ah

        self.mouse = pynput.mouse.Controller()

        self.setWindowFlags(
            Qt.Window |
            Qt.WindowTitleHint |
            Qt.CustomizeWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint
        )

        self.setWindowTitle("Elden Ring Death Counter")

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setGeometry(50, 50, self.aw, self.ah)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        if os.path.exists(fullpath):
            death_count, text_size, text_color, language = search_data_json(fullpath)
        else:
            death_count = 0
            text_size = 45
            text_color = 0
            language = 'en'

        self.language = language
        self.colors = ['red', 'blue', 'yellow', 'black', 'cyan', 'gray', 'white', 'purple']
        self.count = text_color
        self.deaths = death_count
        self.deathsize = text_size
        self.deathcolor = self.colors[self.count]
        self.defaultstyle = "font-weight: 800;"

        self.layout = QVBoxLayout(central_widget)
        self.text = QLabel()
        if self.language == 'en':
            self.text.setText(f"Deaths: {self.deaths}")
        elif self.language == 'br':
            self.text.setText(f"Mortes: {self.deaths}")
        self.text.setStyleSheet(f"font-size: {self.deathsize}px; {self.defaultstyle} color: {self.deathcolor}")
        self.layout.addWidget(self.text)
    
        threading.Thread(target=self.keyboard_listener, daemon=True).start()

        threading.Thread(target=self.screen_listener, daemon=True).start()

    def screen_listener(self):
        screen = f"death_screen_{self.language}.jpg"

        while True:
            death_screen_image = cv2.imread(screen, cv2.IMREAD_ANYCOLOR)
            screenshot = pyag.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            result = cv2.matchTemplate(screenshot, death_screen_image, cv2.TM_CCOEFF_NORMED)

            _, max_val, _, _ = cv2.minMaxLoc(result)

            if max_val > 0.55:
                self.deaths += 1
                self.update_deathcounter()
                time.sleep(2)
            time.sleep(0.25)

    def update_deathcounter(self):
        if self.language == 'br':
            self.text.setText(f"Mortes: {self.deaths}")
        elif self.language == 'en':
            self.text.setText(f"Deaths: {self.deaths}")
        update_json(fullpath, self.deaths, self.deathsize, self.count, self.language)
    
    def update_deathstyle(self):
        self.text.setStyleSheet(f"font-size: {self.deathsize}px; {self.defaultstyle} color: {self.deathcolor}")
        update_json(fullpath, self.deaths, self.deathsize, self.count, self.language)

    def on_press(self, key):
        try:
            if key.char == '-':
                if self.deathsize > 5:
                    self.deathsize -= 5
                    self.update_deathstyle()
                    time.sleep(0.01)  
            elif key.char == '+':
                self.deathsize += 5
                self.update_deathstyle()
                time.sleep(0.01)
        except AttributeError:
            if key == pynput.keyboard.Key.insert:
                self.deaths += 1
                self.update_deathcounter()
            elif key == pynput.keyboard.Key.delete:
                self.deaths -= 1
                self.update_deathcounter()
            elif key == pynput.keyboard.Key.page_up:
                if self.count < len(self.colors)-1:
                    self.count += 1
                else:
                    self.count = 0
                self.deathcolor = self.colors[self.count]
                self.update_deathstyle()
            elif key == pynput.keyboard.Key.page_down:
                if self.count > 0:
                    self.count -= 1
                else:
                    self.count = len(self.colors)-1
                self.deathcolor = self.colors[self.count]
                self.update_deathstyle()
            elif key == pynput.keyboard.Key.f7:
                reset_json(fullpath, self.leaveEvent)
                self.count = 0
                self.deaths = 0
                self.deathsize = 45
                self.update_deathstyle()
                self.update_deathcounter()
            elif key == pynput.keyboard.Key.f11:
                window.close()
        return
    
    def on_release(self, key):
        return

    def keyboard_listener(self):
        with pynput.keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release) as kb:
                kb.join()

    def mouseMoveEvent(self, event):
        xx, yy = self.mouse.position
        self.move(int(xx), int(yy))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    create_json()
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
