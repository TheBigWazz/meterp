import pyaudio
import audioop
from PyQt5 import QtWidgets, QtGui, QtCore
from math import log10

# Import the QPushButton class
from PyQt5.QtWidgets import QPushButton
import sounddevice as sd

# Create the main window
app = QtWidgets.QApplication([])
window = QtWidgets.QWidget()
window.setWindowTitle("Meterp")

# Set the background color and text color for the widget
window.setStyleSheet("""
    QWidget {
        background-color: #2D2D2D;
        color: white;
    }
""")

# Create a label
label = QtWidgets.QLabel(text="")

# Set the text color for the label
label.setStyleSheet("color: white;")

# Create a progress bar
progress_bar = QtWidgets.QProgressBar()

# Set the style for the progress bar
progress_bar.setStyleSheet("""
    QProgressBar {
        background-color: #2D2D2D;
        color: white;
        border: 1px solid black;
        border-radius: 5px;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: green;
        width: 1px;
        margin: 1px;
    }
""")



# Get the list of available devices
p = pyaudio.PyAudio()

devices = {}

# Get the device information
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        name = p.get_device_info_by_host_api_device_index(0, i).get('name')
        devices[name] = i

p.terminate()

# Create a dropdown menu
device_var = QtWidgets.QComboBox()
device_var.addItem("Select Device")  # Add "Select Device" as the default option
device_var.addItems(list(devices.keys()))

# Choose the device and start the stream
device_index = -1  # Set the default device index to -1
if device_var.currentText() != "Select Device":
    device_index = devices[device_var.currentText()]
p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index=device_index, frames_per_buffer=1024)

  

ref = 1
def update_display():
    global device_index, muted
    if not stream.is_active:
        label.setText('MUTED')
        
    else:
        data = stream.read(1024)
        rms = audioop.rms(data, 2)
        try:
            dB = round(20 * log10(rms / ref))
            label.setText(str(dB) + " dB")
            progress_bar.setValue(rms)
        except ValueError:
            label.setText('Muted')
            
    progress_bar.repaint()
    QtCore.QTimer.singleShot(1, update_display)


# Start updating the display
update_display()



def change_device(*args):
    global stream
    global p
    global progress_bar

    # Get the selected device index
    if device_var.currentText() == "Select Device":
        device_index = -1  # Set the device index to -1 if "Select Device" is selected
    else:
        device_index = devices[device_var.currentText()]
    
    if device_index == -1:
        return  # Exit the function if "Select Device" is selected

    # Set the maximum value of the progress bar based on the maximum input channel count
    max_input_channels = p.get_device_info_by_host_api_device_index(0, device_index).get('maxInputChannels')
    if max_input_channels == 1:
        progress_bar.setMaximum(32768)
    else:
        progress_bar.setMaximum(32768 * max_input_channels)

    # Stop and close the current stream
    stream.stop_stream()
    stream.close()

    # Restart the stream with the new device
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index=device_index, frames_per_buffer=1024)

    # Start updating the display
    update_display()

   
# Connect the device dropdown menu's currentIndexChanged signal to the change_device function
device_var.currentIndexChanged.connect(change_device)

# Create a layout for the widgets
layout = QtWidgets.QVBoxLayout()

# Add the widgets to the layout
layout.addWidget(device_var)
layout.addWidget(label)
layout.addWidget(progress_bar)


# Set the layout for the main window
window.setLayout(layout)

# Show the main window
window.show()

# Run the application loop
app.exec_()

# Clean up
stream.stop_stream()
stream.close()
p.terminate()