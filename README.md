# Elden Ring Death Counter
Project made with Python that automatically check if the player died based on the death screen 

## Plans for future updates
- Make an executable file ✔
- Check the save file (.sl2) directly instead using screenshot from pyautogui
- Add more languages support
- Better way to change the main language
- Support to more resolutions
- Easier way to change settings

## How to use
You can follow the Setup area or clone this repo and install all the required libs, when you run the file for the first time will be created a config.json in **C:/Users/(your user)/EldenRingCounter/** in Windows and **~/EldenRingCounter** in Linux based systems, if your game is running on a language different from default (en-us), 
you can change it by going to config file and changing the language

### Supported languages

English: "en-us"
<br>
Portuguese: "pt-br"

### Keybinds

Text color list: ['white', 'blue', 'yellow', 'black', 'cyan', 'gray', 'red', 'purple']

#### You need to hold ALT so the keybinds work
*Example: ALT + Insert*
- **+ (Numpad)** : Increase text size
- **- (Numpad)** : Decrase text size
- **Insert**: Manually add one death to the counter
- **Delete**: Manually remove one death from the counter 
- **PageUp**: Go to the next color in the color list
- **PageDown**: Go to the previous color in the color list
- **End**: Switch the overlay priority
- **F7**: Reset settings to default (Your deaths aswell)
- **F11**: Close the application

# Setup
Created with Pyinstaller to build into an exe and Inno Setup Compiller to make the setup. The setup is very simple, just follow the steps that wizard will ask, then you can run it!
