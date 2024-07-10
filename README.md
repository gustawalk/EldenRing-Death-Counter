# Elden Ring Death Counter
Project made with Python that automatically check if the player died based on the death screen 

## Plans for future updates
- Make an executable file ✔
- Check the save file (.sl2) directly instead using screenshot from pyautogui
- Add more languages support
- Better way to change the main language
- Support to more resolutions

## How to use
You can follow the Setup area or clone this repo and install all the required libs, when you run the file for the first time will be created a config.json in **C:/DeathCounter/**, if your game is running on a language different from default (en), 
you can change it by going to config file and changing the language

### Supported languages

English: "en"
<br>
Portuguese: "br"

### Keybinds

Text color list: ['red', 'blue', 'yellow', 'black', 'cyan', 'gray', 'white', 'purple']
- **+ (Numpad)** : Increase text size
- **- (Numpad)** : Decrase text size
- **Insert**: Manually add one death to the counter
- **Delete**: Manually remove one death from the counter 
- **PageUp**: Go to the next color in the color list
- **PageDown**: Go to the previous color in the color list
- **F7**: Reset settings to default
- **F11**: Close the application

# Setup
Created with Pyinstaller to build into an exe and Inno Setup Compiller to make the setup. The setup is very simple, just follow the steps that wizard will ask, then you can run it!
