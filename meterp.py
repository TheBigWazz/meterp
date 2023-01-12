import pyaudio
import audioop
from PyQt5 import QtWidgets, QtGui, QtCore
from math import log10
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
import sounddevice as sd

# Create the main window
app = QtWidgets.QApplication([])
window = QtWidgets.QWidget()
window.setWindowTitle("MeterP")
window.resize(207,300)

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
progress_bar.setOrientation(Qt.Vertical)
progress_bar.setMaximum(2147483647)
progress_bar.setMinimumWidth(50)

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
        width: 20px;
        height: 1px;
        border: 1px solid black;
        border-radius: 1px;
    }
""")

# Get the list of available devices
p = pyaudio.PyAudio()
devices = {}
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
device_var.setMinimumWidth(85)  # Set the minimum
device_var.setMaximumWidth(125) 
device_var.setStyleSheet("QListView {min-width: 300px;}")

# Choose the device and start the stream
device_index = -1  # Set the default device index to -1
if device_var.currentText() != "Select Device":
    device_index = devices[device_var.currentText()]
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index=device_index, frames_per_buffer=1024)

ref = 1
def update_display():
    global device_index
    data = stream.read(1024)
    rms = audioop.rms(data, 2)
    try:
        dB = round(20 * log10(rms / ref))
        label.setText(str(dB) + " ~ dB")
        progress_bar.setValue(rms)
        progress_bar.setRange(0, 5000)
        print(dB)
    except ValueError as e:
        label.setText('-')
        print(e)
    progress_bar.repaint()
    QtCore.QTimer.singleShot(100, update_display)

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

    # Set the maximum value of the progress bar
    progress_bar.setMaximum(5000)

    # Close the previous stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Open the new stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index=device_index, frames_per_buffer=1024)
    
    # Start updating the display
    update_display()

# Start updating the display
update_display()

# Connect the "currentIndexChanged" signal of the dropdown menu to the "change_device" function
device_var.currentIndexChanged.connect(change_device)

# Create the Layout
layout = QVBoxLayout()
layout.addWidget(progress_bar, alignment=Qt.AlignHCenter)
layout.addWidget(label, alignment=Qt.AlignHCenter)
layout.addWidget(device_var, alignment=Qt.AlignHCenter)
window.setLayout(layout)
window.show()

# Run the application
app.exec_()
