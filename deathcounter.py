import sys
import os
from PyQt5 import *
import pynput
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time
import threading
import numpy as np
import cv2
import json
from pathlib import Path
import mss
import mss.tools
from functools import partial
from screeninfo import get_monitors
import ctypes.wintypes


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
        return data['deaths'], data['text_size'], data['text_color'], data['language'], data['monitor']
    elif filename == "language":
        if language == "pt-br":
            return data['pt-br']['main_text'], data['pt-br']['select_screen'], data['pt-br']['select_language'], data['pt-br']['change_main_text'], data['pt-br']['continue_text']
        elif language == "en-us":
            return data['en-us']['main_text'], data['en-us']['select_screen'], data['en-us']['select_language'], data['en-us']['change_main_text'], data['en-us']['continue_text']

def search_size_json(filepath):
    data = read_json(filepath)
    return data

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
            'language': 'en-us',
            'monitor': 0
        }
        
        with open(filepath, 'w') as file:
            json.dump(data, file)
    elif filename == "language":
        if os.path.exists(filepath):
            return
        data = {
                "pt-br": {
                    "main_text": "Mortes: ",
                    "select_screen": "Escolha o monitor: ",
                    "select_language": "Escolha o idoma do Elden Ring: ",
                    "change_main_text": "Altere o texto antes do contador: ",
                    "continue_text": "Continuar"
                },
                "en-us": {
                    "main_text": "Deaths: ",
                    "select_screen": "Select the monitor: ",
                    "select_language": "Select Elden Ring language: ",
                    "change_main_text": "Change the text before the counter: ",
                    "continue_text": "Continue"
                }
        }

        with open(filepath, 'w') as file:
            json.dump(data, file)

def update_json(filepath, count=0, size=0, color=0, language="", main_monitor=0, main_text="", filename=""):
    if filename == "config":
        data = {
            'deaths': int(count),
            'text_size': int(size),
            'text_color': int(color),
            'language': str(language),
            'monitor': int(main_monitor)
        }
        
        with open(filepath, 'w') as file:
            json.dump(data, file)
    elif filename == "language":
        data = {
            "pt-br": {
                "main_text": main_text,
                "select_screen": "Escolha o monitor: ",
                "select_language": "Escolha o idoma do Elden Ring: ",
                "change_main_text": "Altere o texto antes do contador: ",
                "continue_text": "Continuar"
            },
            "en-us": {
                "main_text": main_text,
                "select_screen": "Select the monitor: ",
                "select_language": "Select Elden Ring language: ",
                "change_main_text": "Change the text before the counter: ",
                "continue_text": "Continue"
            }
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

def get_monitor_info(monitor_number):
    monitors = get_monitors()

    if monitor_number < len(monitors):
        return monitors[monitor_number]
    else:
        raise ValueError(f"Monitor with index {monitor_number} does not exist.")
    
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
        
        self.setWindowIcon(QIcon('icon.ico'))

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setGeometry(50, 50, self.aw, self.ah)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        death_count, text_size, text_color, language, monitor = search_data_json(f"{path}/{config_file}", "config")
        main_text, _, _, _, _ = search_data_json(f"{path}/{language_file}", "language", language)

        self.main_monitor = monitor

        self.overlay_priority = True
        self.language = language
        self.main_text = main_text
        self.colors = ['white', 'blue', 'yellow', 'black', 'cyan', 'gray', 'red', 'purple']
        self.colorindex = text_color
        self.deaths = death_count
        self.textsize = text_size
        self.deathcolor = self.colors[self.colorindex]
        self.defaultstyle = "font-weight: 800;"

        self.layout = QVBoxLayout(central_widget)
        self.text = QLabel()
        self.text.setText(f"{self.main_text}{self.deaths}")
        self.text.setStyleSheet(f"font-size: {self.textsize}px; {self.defaultstyle} color: {self.deathcolor}")
        self.layout.addWidget(self.text)
    
        threading.Thread(target=self.keyboard_listener, daemon=True).start()

        threading.Thread(target=self.screen_listener, daemon=True).start()

    
    def screen_listener(self):
        screen = f"death_screen_{self.language}.jpg"

        monitor = get_monitor_info(self.main_monitor)
        sct = mss.mss()

        monitor_region = {
            "left": monitor.x,
            "top": monitor.y,
            "width": monitor.width,
            "height": monitor.height
        }

        while True:
            death_screen_image = cv2.imread(screen, cv2.IMREAD_COLOR)
            
            if death_screen_image.dtype != np.uint8:
                death_screen_image = cv2.convertScaleAbs(death_screen_image)
            
            monitor_region = {
                "left": monitor.x,
                "top": monitor.y,
                "width": monitor.width,
                "height": monitor.height
            }
            
            screenshot = sct.grab(monitor_region)
            
            screenshot = np.array(screenshot)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            
            if screenshot.dtype != np.uint8:
                screenshot = cv2.convertScaleAbs(screenshot)
        
            result = cv2.matchTemplate(screenshot, death_screen_image, cv2.TM_CCOEFF_NORMED)
            
            _, max_val, _, _ = cv2.minMaxLoc(result)

            if max_val > 0.55:
                self.deaths += 1
                self.update_deathcounter()
                time.sleep(2)
            time.sleep(0.25)

    def update_deathcounter(self):
        self.text.setText(f"{self.main_text}{self.deaths}")
        update_json(f"{path}/{config_file}", self.deaths, self.textsize, self.colorindex, self.language, filename='config')
    
    def update_deathstyle(self):
        self.text.setStyleSheet(f"font-size: {self.textsize}px; {self.defaultstyle} color: {self.deathcolor}")
        update_json(f"{path}/{config_file}", self.deaths, self.textsize, self.colorindex, self.language, filename='config')

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
                    reset_json(f"{path}/{config_file}", self.language)
                    self.colorindex = 0
                    self.deaths = 0
                    self.textsize = 45
                    self.update_deathstyle()
                    self.update_deathcounter()
                elif key == pynput.keyboard.Key.end:
                    self.change_priority()
                elif key == pynput.keyboard.Key.f11:
                    self.close()
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

class ConfigWindow(QDialog):
    saveConfigSignal = pyqtSignal()

    def __init__(self, aw, ah):
        super().__init__()

        self.setWindowTitle("ER Counter Configuration")
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.aw = aw
        self.ah = ah

        self.death, self.text_size, self.text_color, self.language, self.main_monitor = search_data_json(f"{path}/{config_file}", "config")
        self.main_monitor_name = get_monitor_info(self.main_monitor)

        main_text, select_screen, select_language, change_main_text, continue_text = search_data_json(f"{path}/{language_file}", "language", self.language)

        view = QApplication.desktop().screenGeometry()
        scr_width = int((view.width() / 2) - (aw / 2))
        scr_height = int((view.height() / 2) - (ah / 2))
        self.setGeometry(scr_width, scr_height, aw, ah)

        self.layout = QFormLayout()
        
        self.select_monitor = QLabel(select_screen)
        self.layout.addWidget(self.select_monitor)

        self.monitor_group = QButtonGroup()
        for monitor in get_monitors():
            self.monitors = QRadioButton(f"{monitor.name}")
            self.monitors.clicked.connect(partial(self.radio_monitor_button_clicked, monitor.name))
            self.layout.addWidget(self.monitors)
            self.monitor_group.addButton(self.monitors)

            if monitor.name == self.main_monitor_name.name:
                self.monitors.setChecked(True)

        self.select_language = QLabel(select_language)
        self.layout.addWidget(self.select_language)

        lang_options = search_size_json(f"{path}/{language_file}")

        self.language_group = QButtonGroup()
        for lang in lang_options:
            self.languages = QRadioButton(f"{lang}")
            self.languages.clicked.connect(partial(self.radio_lang_button_clicked, lang))
            self.layout.addWidget(self.languages)
            self.language_group.addButton(self.languages)

            if lang == self.language:
                self.languages.setChecked(True)

        self.change_maintext = QLabel(change_main_text)
        self.layout.addWidget(self.change_maintext)

        self.maintext_area = QTextEdit(main_text)
        self.maintext_area.setStyleSheet("max-height: 30px;")
        self.layout.addWidget(self.maintext_area)

        self.save_button = QPushButton(continue_text)
        self.save_button.clicked.connect(self.update_all_config)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        quit = QAction("Quit", self)
        quit.triggered.connect(self.close)

    def radio_lang_button_clicked(self, language):
        self.update_main_language(language)
    
    def update_main_language(self, language):
        update_json(f"{path}/{config_file}", self.death, self.text_size, self.text_color, language, self.main_monitor, filename='config')
        self.language = language
        main_text, select_screen, select_language, change_main_text, continue_text = search_data_json(f"{path}/{language_file}", "language", language)

        self.select_monitor.setText(select_screen)
        self.select_language.setText(select_language)
        self.change_maintext.setText(change_main_text)
        self.maintext_area.setText(main_text)
        self.save_button.setText(continue_text)

    def radio_monitor_button_clicked(self, name):
        self.update_main_monitor(name)

    def update_main_monitor(self, name):
        name = name[11:]
        name = int(name)
        name = name-1
        self.main_monitor = name
    
    def update_all_config(self):
        main_text, _, _, _, _ = search_data_json(f"{path}/{language_file}", "language", self.language)
        new_main_text = self.maintext_area.toPlainText()

        if new_main_text != main_text:
            update_json(f"{path}/{language_file}", main_text= new_main_text, filename="language")

        update_json(f"{path}/{config_file}", self.death, self.text_size, self.text_color, self.language, self.main_monitor, filename="config")

        self.saveConfigSignal.emit()
        self.close()

class Application(QApplication):
    def __init__(self, *args):
        super().__init__(*args)

        self.create_initial_config_files()

        self.config_window = ConfigWindow(300, 300)
        self.config_window.show()

        self.config_window.saveConfigSignal.connect(self.show_main_window)

    def create_initial_config_files(self):
        create_json(f"{path}/{config_file}", "config")
        create_json(f"{path}/{language_file}", "language")

    def show_main_window(self):
        self.config_window.close()
        self.main_window = MainWindow()
        self.main_window.show()

if __name__ == '__main__':
    app = Application(sys.argv)
    sys.exit(app.exec_())
