import pyaudio
import struct
import math
import tkinter as tk

# Set up tkinter
root = tk.Tk()
root.title("Audio Level Meter")
root.configure(background="gray")

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
bar = tk.Canvas(root, width=BAR_WIDTH + 50, height=400)
bar.config(bg='dark gray')
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
    format = p.get_format_from_width(WIDTH)
    max_amplitude = 2**(p.get_sample_size(format)*8 - 1)
    max_db = 20 * math.log10(max_amplitude)
    
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
    db = 20 * math.log10(rms)
    
    # Scale the RMS level to a value between 0 and BAR_HEIGHT
    bar_level = int((db / max_db) * BAR_HEIGHT)
    if bar_level > BAR_HEIGHT:
        bar_level = BAR_HEIGHT
        
    # Update the bar graph
    bar.delete("all")
    bar.create_rectangle(0, BAR_HEIGHT - bar_level, BAR_WIDTH, BAR_HEIGHT, fill="green")
    bar.create_rectangle(0, 0, BAR_WIDTH, BAR_HEIGHT - bar_level, fill="dark gray")
    
    # Add dB markings
    for i in range(0, math.floor(max_db) + 1, 10):
        y = BAR_HEIGHT - int((i / math.floor(max_db)) * BAR_HEIGHT) + 20
        bar.create_line(BAR_WIDTH - 10, y, BAR_WIDTH + 1, y, fill="black")
        bar.create_text(BAR_WIDTH + 10, y, text=str(i) + " dB", anchor="w", fill="black")
    
    # Schedule the next update
    root.after(50, update_bar)
    
# Get a list of available input devices
device_options = ["None"]
for i in range(p.get_device_count()):
    device_info = p.get_device_info_by_index(i)
    if device_info["maxInputChannels"] > 0:
        device_options.append(device_info["name"])

# Create the device selection button and label
device_label = tk.Label(root, text="")
device_label.pack()
device_var = tk.StringVar(root)
device_var.set(device_options[1])
open_device()

# Create the drop-down menu for selecting the input device
device_menu = tk.OptionMenu(root, device_var, *device_options)
device_menu.pack()

# Create the "Open Device" button
open_button = tk.Button(root, text="Load Device", command=open_device)
open_button.pack()

# Start the main loop
root.mainloop()

# Clean up
if stream is not None:
    stream.stop_stream()
    stream.close()
p.terminate()