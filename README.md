# meterp
A digital level meter for input devices

![image](https://user-images.githubusercontent.com/80355486/212165935-77cb0f6d-ca79-42ff-864a-db403be1d546.png)

## Notes 
- Actual dB readout is approximate. This tool should not be used for accurate measurements.
- If an input device becomes muted (or silent in the case of noise removal applications), the readout shows ```-```
- Consumes 16mb RAM and ~ 0.5% CPU

# Compiling
Follow the instructions below to compile the program yourself, or download the .exe release. 

### Dependencies

### Python: 

#### Windows ####
 
https://www.python.org/downloads/  
**Make sure to check the box that adds Python to your PATH before installing*  

#### Debian ####

```sudo apt install python3```  
___

### PyQt5: ###  
```pip install PyQt5```

### PyAudio: ###
```pip install pyaudio```

### sounddevice: ###
```pip install sounddevice```

### PyInstaller: ###  
```pip install pyinstaller```


# Creating Executable 
Navigate to where meterp.py is saved and run this command:  
```pyinstaller --windowed meterp.py -F```
  
> --windowed: Hides the Python console when running the application

> -F: Packages everything needed for the application to run into a single executable. The file is output in the 'dist' folder created in the same location as the script.

View more information about PyInstaller to further customize the executable: https://pyinstaller.org/en/stable/

# Executable Shortcuts
### Windows
- Right click the EXE created and send a shortcut to the desktop. 
- If you'd like, right click the shortcut and set the icon to chatgpt.ico (provided)
- If you'd like, right click the shortcut and rename it.

At this point you can pin the shortcut to the taskbar or start menu, or leave it on the desktop.

### Debian
- Update the meterp.desktop file with the correct paths to the executable and icon. Lines 4 and 5:
```
[Desktop Entry]
Type=Application
Name=MeterP
Exec=/(Location to executable)
Icon=/(Location to)/chatgpt.ico
```

- Move MeterP.desktop to this location:
> ~/.local/share/applications

At this point you should be able to find 'MeterP' with your preferred application launcher and move it various places depending on your Desktop Enviorment.
