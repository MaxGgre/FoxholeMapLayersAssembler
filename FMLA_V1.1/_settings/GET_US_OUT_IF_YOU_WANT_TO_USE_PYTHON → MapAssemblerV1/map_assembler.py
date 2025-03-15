import os
import subprocess
import sys

version = "1.1"

print("Current working directory:", os.getcwd())

# Function to install a package if it's not already installed
def install_package(package_name):
    try:
        __import__(package_name)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])

# Install Pillow if not already installed
install_package('Pillow')

# Install requests if not already installed
install_package('requests')

from PIL import Image
import requests
import re
import json
import tkinter as tk
from tkinter import Frame, Listbox, Scrollbar, BooleanVar, messagebox, PhotoImage

json_file_path = "_settings/item_codes.json"

with open(json_file_path, 'r') as json_file:
    item_code_dict = json.load(json_file)

json_file_path = '_settings/map_list.json'

with open(json_file_path, 'r') as json_file:
    cached_map = json.load(json_file)

itemfolder = "ItemLayers"
dicfolder = "DataDics"
mapfolder = "BaseMaps"
globalfolder = "GlobalLayers"
spefolder = "SpeLayers"
item_list = []
live = "https://war-service-live.foxholeservices.com/api"

def file_name(item):
    match = re.match(r'(.+)(\.[^.]+)$', item)
    if match:
        return match.group(1)
    return False

def get_top_coords(support: Image, sticker: Image, center_coords: tuple[int, int]) -> tuple[int, int]:

    support_width, support_height = support.size
    sticker_width, sticker_height = sticker.size

    x = support_width * center_coords[0]
    y = support_height * center_coords[1]
    
    x = int(x - sticker_width // 2)
    y = int(y - sticker_height // 2)

    return (x,y)

def sequential_items(mapitem, checkbox_states, show_maps):
    Foxholemap = mapitem[3:-4]
    if Foxholemap == "ClahstraHexMap":
        Foxholemap = "ClahstraHex"
    if Foxholemap == "DeadlandsHex":
        Foxholemap = "DeadLandsHex"
    print(Foxholemap)

    # Load the main image
    background_map = Image.open(os.path.join("BaseMaps/", mapitem)).convert("RGBA")

    if checkbox_states[4][0]:
        new_width = checkbox_states[4][1]
        new_height = checkbox_states[4][2]
        background_map = background_map.resize((new_width, new_height), Image.LANCZOS)

    # Create a blank image of the same size
    image_blank = Image.new("RGBA", background_map.size)
    image_blank = image_blank.convert("RGBA")

    # Get hex data with API request
    staticmap_url = live + "/worldconquest/maps/" + Foxholemap + "/dynamic/public"
    response = requests.get(staticmap_url)

    if Foxholemap == "ClahstraHex":
        Foxholemap = "ClahstraHexMap"
    if Foxholemap == "DeadLandsHex":
        Foxholemap = "DeadlandsHex"

    # Open Correction File
    with open("_settings/correction_in_meters.txt", "r", encoding='utf-8') as fichier:
        corrections = fichier.read()

        #-------------------------------------------------------------------------------------------------------------------------------
    if checkbox_states[3]: #roads and stuff
        # Add the map specific layers
        for root, dirs, files in os.walk(spefolder):
            for layers in files:
                if layers.startswith("Map" + Foxholemap):
                    image2 = Image.open(os.path.join(root, layers)).convert("RGBA")
                    image2 = image2.resize(image_blank.size, Image.LANCZOS)

                    image_blank = Image.alpha_composite(image_blank, image2)

                #-------------------------------------------------------------------------------------------------------------------------------

    if checkbox_states[2]: #borders and else
        # Add the generic layers
        for layers in os.listdir(globalfolder):
            image2 = Image.open(os.path.join(globalfolder, layers)).convert("RGBA")
            image2 = image2.resize(image_blank.size, Image.LANCZOS)

            image_blank = Image.alpha_composite(image_blank, image2)

    if checkbox_states[0]: #items API
        #-------------------------------------------------------------------------------------------------------------------------------
        if response.status_code == 200:
            data = response.json()
        
            # Build item lists
            for item in os.listdir(itemfolder):
                if file_name(item) in item_code_dict:
                    named_item = file_name(item)
                    item_list.append(named_item)
                    numbered_items_list = item_code_dict[named_item]
                    
                else:
                    continue

                for numbered_items in numbered_items_list:
                    # Items presence + coordinate
                    coordinates = [(item['x'], item['y']) for item in data['mapItems'] if item['iconType'] == numbered_items]

                    # Load the smaller image to overlay
                    pic_to_add = Image.open(os.path.join(itemfolder, item)).convert("RGBA")
    
                    xa = 0
                    ya = 0
    
            #-------------------------------------------------------------------------------------------------------------------------------
    
                    # Look for corrections
                    pattern = rf"{numbered_items}\s*:\s*\(([^;]+);([^)]+)\)"
    
                    # Search for coordinates
                    match = re.search(pattern, corrections)
    
                    if match:
                        xa = match.group(1)
                        ya = match.group(2)
    
                        # Corrected coordinates
                        xa = int(xa) * 0.94
                        ya = int(xa) * 0.94
    
    
                    image_temp = Image.new("RGBA", image_blank.size, (255, 255, 255, 0))
                    for coords in coordinates:
    
                        coords = get_top_coords(image_temp, pic_to_add, coords)
                        coords = (int(coords[0] + xa),int(coords[1] + ya))
                        
                        image_temp.alpha_composite(pic_to_add, dest= coords)
    
                    image_blank = Image.alpha_composite(image_blank, image_temp)

        else:
            print(f"Error: {Foxholemap} : {response.status_code}")

        #-------------------------------------------------------------------------------------------------------------------------------

    if checkbox_states[1]: 

        # Additional items
        for files in os.listdir(dicfolder):
            newitem = files[:-4]
            new_item_len = len(newitem)

            for pngfiles in os.listdir(itemfolder):
                if pngfiles.startswith(newitem):
                    file_full_name = pngfiles
                    pic_to_add = Image.open(os.path.join(itemfolder, file_full_name)).convert("RGBA")

                    with open(os.path.join(dicfolder, files), "r", encoding='utf-8') as fichier:
                        itemcontent = fichier.read()
                    pattern = rf'{Foxholemap}\s*:\s*\[(.*?)\]'

                    # Search for tuples
                    match = re.search(pattern, itemcontent, re.DOTALL)

                    if match:
                        # Extract tuples as strings
                        tuples_str = match.group(1)
                        #print(tuples_str)
                        # Find all tuples between parentheses
                        tuples = re.findall(r'\((.*?)\)', tuples_str)
                        # Convert strings to tuples of floats
                        tuples = [tuple(map(float, t.split(','))) for t in tuples]

                        image_temp = Image.new("RGBA", image_blank.size, (255, 255, 255, 0))
                        for coords in tuples:

                            print(file_full_name, coords)

                            image_temp.alpha_composite(pic_to_add, dest= get_top_coords(image_temp, pic_to_add, coords))

                        image_blank = Image.alpha_composite(image_blank, image_temp)

                else:
                    continue

    # Composite the blank image with the background map
    final_image = Image.alpha_composite(background_map, image_blank)

    # Save or display the resulting images
    final_image.save(f'Result/{mapitem}')
    image_blank.save(f'Result/blank_result/blank_{mapitem}')

    if show_maps:
        final_image.show()

    return item_list

# Function to center the window and set its size to 75% of the screen height and 40% of the screen width
def center_window(window, width_percent=35, height_percent=80):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    width = int(screen_width * width_percent / 100)
    height = int(screen_height * height_percent / 100)

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    window.geometry(f'{width}x{height}+{x}+{y}')

# Function to execute processing when the button is clicked
def execute_processing():
    checkbox_states = [var.get() for var in check_vars]
    override_tuple = (override_var.get(), x_value, y_value)  # Create a tuple with override state and size values
    checkbox_states.append(override_tuple)  # Add the tuple to checkbox_states
    show_maps = show_maps_var.get()

    for mapitem in os.listdir(mapfolder):
        sequential_items(mapitem, checkbox_states, show_maps)
    messagebox.showinfo("Information", "Processing complete!")
    root.destroy()

# Function to read map size override values from file
def read_map_size_override():
    try:
        with open('_settings/map_size_override.txt', 'r') as file:
            lines = file.readlines()
            x_value = int(lines[0].split('=')[1].strip())
            y_value = int(lines[1].split('=')[1].strip())
        return x_value, y_value
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read map size override values: {e}")
        return 0, 0

# Create the main window
root = tk.Tk()
root.title("Foxhole Map Layers Tool")

# Center the window and set its size
center_window(root)

# Configure styles
root.configure(bg='#f0f0f0')
style = {
    'font': ("Jost", 12),
    'bg': '#ffffff',
    'fg': '#333333'
}

# Create a frame to organize elements
main_frame = Frame(root, bg='#f0f0f0')
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Add titles and lists for each segment
segments = [
    ("Detected Items", os.listdir(itemfolder)),
    ("Detected Dics", os.listdir(dicfolder)),
    ("Detected Global Layers", os.listdir("GlobalLayers")),
    ("Detected SpeLayers", os.listdir("SpeLayers"))
]

# Variables for checkboxes
check_vars = [BooleanVar() for _ in segments]

for i, (title, items) in enumerate(segments):
    label = tk.Label(main_frame, text=title, font=("Jost", 13, "bold"), bg='#f0f0f0', fg='#333333')
    label.grid(row=i*3, column=0, sticky="w", pady=(0, 2), padx=(5, 0))

    # Add the checkbox in the first column
    checkbox = tk.Checkbutton(main_frame, text="Enable", variable=check_vars[i], bg='#f0f0f0')
    checkbox.grid(row=i*3, column=1, sticky="w", padx=(5, 0))

    # Add the note in small gray text in the second column
    if title == "Detected Items":
        note_label = tk.Label(main_frame, text="(may use WarAPI => won't work if no war on Able)", font=("Jost", 10), bg='#f0f0f0', fg='#888888')
        note_label.grid(row=i*3, column=2, sticky="w", padx=(5, 0))

    if title == "Detected Dics":
        note_label = tk.Label(main_frame, text="(Make sure there is corresponding image in detected items!!)", font=("Jost", 10), bg='#f0f0f0', fg='#888888')
        note_label.grid(row=i*3, column=2, sticky="w", padx=(5, 0))

    listbox = Listbox(main_frame, height=5, width=50, **style)
    listbox.grid(row=i*3+1, column=0, sticky="w", columnspan=3, padx=(5, 0), pady=(0, 10))

    scrollbar = Scrollbar(main_frame, orient="vertical", command=listbox.yview)
    scrollbar.grid(row=i*3+1, column=3, sticky="ns", padx=(0, 5))
    listbox.config(yscrollcommand=scrollbar.set)

    for item in items:
        listbox.insert(tk.END, item)

# Read map size override values
x_value, y_value = read_map_size_override()

# Add map size override labels and checkbox
override_frame = Frame(main_frame, bg='#f0f0f0')
override_frame.grid(row=len(segments)*3, column=0, columnspan=3, pady=(10, 0))

override_label = tk.Label(override_frame, text="Map Size Override", font=("Jost", 13, "bold"), bg='#f0f0f0', fg='#333333')
override_label.pack(anchor="w")

size_label = tk.Label(override_frame, text=f"{x_value} x {y_value}", font=("Jost", 12), bg='#f0f0f0', fg='#333333')
size_label.pack(anchor="w")

override_var = BooleanVar()
override_checkbox = tk.Checkbutton(override_frame, text="Override size?", variable=override_var, bg='#f0f0f0')
override_checkbox.pack(anchor="w")

# Add a note about modifying the override in settings
override_note = tk.Label(main_frame, text="Note: Override values can be modified in the settings.", font=("Jost", 10, "italic"), bg='#f0f0f0', fg='#555555')
override_note.grid(row=len(segments)*3+1, column=0, columnspan=3, pady=(5, 0))

# Create a frame for the button and checkbox
button_frame = Frame(root, bg='#f0f0f0')
button_frame.pack(pady=20)

# Add a button to execute processing
execute_button = tk.Button(button_frame, text="Generate Maps", command=execute_processing, font=("Jost", 12, "bold"), bg='#4CAF50', fg='white')
execute_button.pack(side="left", padx=10)

# Add a checkbox for "Show maps during processing"
show_maps_var = BooleanVar()
show_maps_checkbox = tk.Checkbutton(button_frame, text="Show maps?", variable=show_maps_var, bg='#f0f0f0')
show_maps_checkbox.pack(side="left")



# Add a signature with a logo on the right
signature_frame = Frame(root, bg='#f0f0f0')
signature_frame.place(relx=1.0, rely=1.0, anchor="se")

# Load and display the logo
logo_image = PhotoImage(file="_settings/logo.png")  # Ensure 'logo.png' is in the same directory as your script
logo_label = tk.Label(signature_frame, image=logo_image, bg='#f0f0f0')
logo_label.pack(side="right")

signature = tk.Label(signature_frame, text="Provided by KoV V"+version, font=("Jost", 10, "italic"), bg='#f0f0f0', fg='#555555')
signature.pack(side="right", padx=5)

# Run the main application loop
root.mainloop()
