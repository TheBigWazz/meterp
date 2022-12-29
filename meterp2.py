import pyaudio
import struct
import math
import tkinter as tk
from functools import partial  # Import partial from functools

# Set up tkinter
root = tk.Tk()
root.title("Audio Level Meter")
root.configure(background="#181818")  # Change background color to YouTube dark mode color

# Set up pyaudio
p = pyaudio.PyAudio()

# Set up the input stream
CHUNK = 1024
WIDTH = 2
CHANNELS = 1
RATE = 44100

# Define the global stream variable
global stream
stream = None

# Set up the visualizer
BAR_WIDTH = 20
BAR_HEIGHT = 400

# Create the bar graph widget
bar = tk.Canvas(root, width=BAR_WIDTH + 50, height=400, highlightthickness=0)  # Remove highlightthickness to remove white border
bar.config(bg='#181818')  # Change background color to YouTube dark mode color
bar.pack()



# Function to open the selected input device
def open_device():
    global stream
    global max_db
    device_index = None
    device_name = device_var.get()
    if device_name == "None":
        return
    device_index = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info["name"] == device_name:
            device_index = device_info["index"]
            break
    if device_index is None:
        return
    if stream is not None:
        stream.stop_stream()
        stream.close()
    stream = p.open(
        format=p.get_format_from_width(WIDTH),
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=False,
        input_device_index=device_index,
        frames_per_buffer=CHUNK,
    )
        # Get the maximum dB level of the input device
    max_db =  80
        
    # Update the bar graph
    if max_db:  # Check if max_db is defined
        update_bar()
    
    
    
# Function to update the bar graph
def update_bar():
    # Read data from the input stream
    data = stream.read(CHUNK)
    data = struct.unpack(str(CHUNK) + 'h', data)

    # Calculate the RMS level of the audio
    rms = math.sqrt(sum(x ** 2 for x in data) / len(data))
    # Calculate the SPL in dB relative to a reference value of 0 dB
    
    reference = 20  # Reference value for SPL in pascals
    db = math.log10(rms / reference) - 0  # Subtract 0 dB to make the reference value 0 dB
    
    if db > max_db:
        db = max_db

    # Calculate the bar level on a non-logarithmic scale
    bar_level = int((db / 80) * BAR_HEIGHT)
    if bar_level > BAR_HEIGHT - 20:  # Leave room for the dB markings
        bar_level = BAR_HEIGHT - 20

    # Update the bar graph
    bar.delete("all")
    bar.create_rectangle(0, BAR_HEIGHT - bar_level, BAR_WIDTH, BAR_HEIGHT, fill="#00ff00")
    bar.create_rectangle(0, 0, BAR_WIDTH, BAR_HEIGHT - bar_level, fill="#181818")

    # Add dB markings
    for i in range(0, int(max_db) + 1, 10):
        y = (i / 80) * BAR_HEIGHT  # Calculate y position based on the dB value
        bar.create_line(BAR_WIDTH - 10, y, BAR_WIDTH + 1, y, fill="#fff")
        bar.create_text(BAR_WIDTH + 10, y, text=str(i) + " dB", anchor="w", fill="#fff")
    
    # Schedule the next update
    root.after(50, update_bar)



# Get a list of available input devices
device_options = ["None"]
for i in range(p.get_device_count()):
    device_info = p.get_device_info_by_index(i)
    device_options.append(device_info["name"])

# Set the default input device
device_var = tk.StringVar(root)
device_var.set(device_options[0])

# Create the device selection menu
device_menu = tk.OptionMenu(root, device_var, *device_options, command=partial(open_device))  # Use partial to create new function that calls open_device with no arguments
device_menu.config(bg="#181818", fg="#fff", activebackground="#303030", activeforeground="#fff", highlightthickness=0)  # Change colors to YouTube dark mode colors
device_menu.pack()

# Create the open device button
open_button = tk.Button(root, text="Open Device", command=partial(open_device))  # Use partial to create new function that calls open_device with no arguments
open_button.config(bg="#181818", fg="#fff", activebackground="#303030", activeforeground="#fff", highlightthickness=0)  # Change colors to YouTube dark mode colors
open_button.pack()

# Start the tkinter event loop
root.mainloop()