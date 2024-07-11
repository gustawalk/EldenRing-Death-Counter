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
from pathlib import Path

home = Path.home()
path = f"{home}/EldenRingCounter/"
config_file = "config.json"
language_file = "lang.json"

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

def search_data_json(filepath, filename, language=""):
    data = read_json(filepath)
    
    if filename == "config":
        return data['deaths'], data['text_size'], data['text_color'], data['language']
    elif filename == "language":
        if language == "pt-br":
            return data['pt-br']['main_text']
        elif language == "en-us":
            return data['en-us']['main_text']


def create_json(filepath, filename):

    if not os.path.exists(path):
        os.mkdir(path)

    if filename == "config":
        if os.path.exists(filepath):
            return
        data = {
            'deaths': 0,
            'text_size': 45,
            'text_color': 0,
            'language': 'en-us'
        }
        
        with open(filepath, 'w') as file:
            json.dump(data, file)
    elif filename == "language":
        if os.path.exists(filepath):
            return
        data = {
                "pt-br": {
                    "main_text": "Mortes: "
                },
                "en-us": {
                    "main_text": "Deaths: "
                }
            }

        with open(filepath, 'w') as file:
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

        self.alt_pressed = False

        self.setWindowTitle("Elden Ring Death Counter")

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setGeometry(50, 50, self.aw, self.ah)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)


        death_count, text_size, text_color, language = search_data_json(f"{path}/{config_file}", "config")

        lang_text = search_data_json(f"{path}/{language_file}", "language", language)

        self.overlay_priority = True
        self.language = language
        self.lang_text = lang_text
        self.colors = ['white', 'blue', 'yellow', 'black', 'cyan', 'gray', 'red', 'purple']
        self.colorindex = text_color
        self.deaths = death_count
        self.textsize = text_size
        self.deathcolor = self.colors[self.colorindex]
        self.defaultstyle = "font-weight: 800;"

        self.layout = QVBoxLayout(central_widget)
        self.text = QLabel()
        self.text.setText(f"{self.lang_text}{self.deaths}")
        self.text.setStyleSheet(f"font-size: {self.textsize}px; {self.defaultstyle} color: {self.deathcolor}")
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
            if max_val > 0.6:
                self.deaths += 1
                self.update_deathcounter()
                time.sleep(2)
            time.sleep(0.25)

    def update_deathcounter(self):
        self.text.setText(f"{self.lang_text}{self.deaths}")
        update_json(f"{path}/{config_file}", self.deaths, self.textsize, self.colorindex, self.language)
    
    def update_deathstyle(self):
        self.text.setStyleSheet(f"font-size: {self.textsize}px; {self.defaultstyle} color: {self.deathcolor}")
        update_json(f"{path}/{config_file}", self.deaths, self.textsize, self.colorindex, self.language)

    def change_priority(self):
        self.overlay_priority = not self.overlay_priority

        if self.overlay_priority:
            self.setWindowFlags(
                Qt.Window |
                Qt.WindowTitleHint |
                Qt.CustomizeWindowHint |
                Qt.WindowStaysOnTopHint |
                Qt.FramelessWindowHint
            )
            self.show()
            self.showNormal()
        else:
            self.setWindowFlags(
                Qt.Window |
                Qt.WindowTitleHint |
                Qt.CustomizeWindowHint |
                Qt.FramelessWindowHint
            )   
            self.show()
            self.showNormal()
            self.showMinimized()

    def on_press(self, key):

        if key == pynput.keyboard.Key.alt_l:
            if self.alt_pressed == False:
                self.alt_pressed = True
            else:
                return

        if self.alt_pressed:
            try:
                if key.char == '-':
                    if self.textsize > 5:
                        self.textsize -= 5
                        self.update_deathstyle()
                        time.sleep(0.01)  
                elif key.char == '+':
                    self.textsize += 5
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
                    if self.colorindex < len(self.colors)-1:
                        self.colorindex += 1
                    else:
                        self.colorindex = 0
                    self.deathcolor = self.colors[self.colorindex]
                    self.update_deathstyle()
                elif key == pynput.keyboard.Key.page_down:
                    if self.colorindex > 0:
                        self.colorindex -= 1
                    else:
                        self.colorindex = len(self.colors)-1
                    self.deathcolor = self.colors[self.colorindex]
                    self.update_deathstyle()
                elif key == pynput.keyboard.Key.f7:
                    reset_json(f"{path}/{config_file}", self.leaveEvent)
                    self.colorindex = 0
                    self.deaths = 0
                    self.textsize = 45
                    self.update_deathstyle()
                    self.update_deathcounter()
                elif key == pynput.keyboard.Key.end:
                    self.change_priority()
                elif key == pynput.keyboard.Key.f11:
                    window.close()
        return
    
    def on_release(self, key):
        if key == pynput.keyboard.Key.alt_l:
            self.alt_pressed = False
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
    create_json(f"{path}/{config_file}", "config")
    create_json(f"{path}/{language_file}", "language")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())