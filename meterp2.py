import pyaudio
import audioop
from PyQt5 import QtWidgets, QtGui, QtCore

# Create the main window
app = QtWidgets.QApplication([])
window = QtWidgets.QWidget()
window.setWindowTitle("Decibel Meter")

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
        border: 1px solid white;
        border-radius: 5px;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: white;
        width: 10px;
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
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True,
                input_device_index=device_index, frames_per_buffer=1024)



# Define a function to update the label and progress bar
def update_display():
    global device_index
    
    # Calculate the RMS and update the label
    data = stream.read(1024)
    rms = audioop.rms(data, 2)
    label.setText(str(rms))
    
    # Update the progress bar
    progress_bar.setValue(rms)
    progress_bar.repaint()
    QtCore.QTimer.singleShot(100, update_display)  # Call this function again in 100ms



# Start updating the display
update_display()



# Define a function to change the device
def change_device(*args):
    global stream
    global p
    global progress_bar

    # Stop and close the current stream
    stream.stop_stream()
    stream.close()

    # Get the selected device index
    if device_var.currentText() == "Select Device":
        device_index = -1  # Set the device index to -1 if "Select Device" is selected
    else:
        device_index = devices[device_var.currentText()]

    # Set the maximum value of the progress bar based on the maximum input channel count
    max_input_channels = p.get_device_info_by_host_api_device_index(0, device_index).get('maxInputChannels')
    if max_input_channels == 1:
        progress_bar.setMaximum(32768)
    else:
        progress_bar.setMaximum(32768 * max_input_channels)

    # Create a new stream with the selected device
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True,
                    input_device_index=device_index, frames_per_buffer=1024)




# Bind the function to the "currentIndexChanged" event
device_var.currentIndexChanged.connect(change_device)

# Create a layout and add the widgets
layout = QtWidgets.QVBoxLayout()
layout.addWidget(device_var)
layout.addWidget(label)
layout.addWidget(progress_bar)
window.setLayout(layout)

# Show the window
window.show()

# Run the PyQt event loop
app.exec_()

# Clean up
stream.stop_stream()
stream.close()
p.terminate()