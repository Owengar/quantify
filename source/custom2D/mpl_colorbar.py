import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import io
import pygame
from PIL import Image
import sys
import json
import time
# Create a figure and axis for the colorbar
#fig, ax = plt.subplots()  # Adjust size as needed
_fig = plt.figure()
_ax = plt.axes((0, 0, 0.2, 1))
_delay = 2

def make_colorbar_surf(color_min, color_max, label : str = ""):
    global _fig, _ax



    _fig.clear()
    #_ax = plt.axes((0, 0, 0.2, 1))  
    #_ax = plt.axes((0, 0, 0.2, 1))  
    #_ax = plt.axes((0, 0, 0.2, 1))
    #_fig.clear()
    # Create a ScalarMappable object to generate a colorbar
    norm = plt.Normalize(vmin=color_min, vmax=color_max)
    cmap = cm.viridis
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)


    # Add the colorbar to the figure
    bar = _fig.colorbar(sm, ax=_ax)
    bar.set_label(label=label, size=14, weight='bold', family='serif')
    # Remove the axis (so only the colorbar is visible)
    #ax.set_axis_off()
    #_ax.remove()


    # Create a BytesIO buffer to hold the image
    buffer = io.BytesIO()

    # Save the figure to the buffer instead of a file
    plt.savefig(buffer, format='jpg', bbox_inches='tight', pad_inches=0.05, transparent=True)







    # Open the image using PIL to get its size and to ensure it's in the correct format
    image = Image.open(buffer)

    # Get the dimensions and convert the image to the appropriate format
    width, height = image.size

    # Convert the image to a format Pygame can use (RGBA or RGB)
    image_data = np.array(image.convert('RGBA'))  # Convert image to RGBA format

    # Convert the numpy array to a bytes buffer (Pygame expects byte format)
    image_data_bytes = image_data.tobytes()

    # Create a pygame surface from the byte data
    surface = pygame.image.frombuffer(image_data_bytes, (width, height), 'RGBA')
    pygame.draw.rect(surface, (0, 0, 0, 255), (0, 0, surface.size[0], surface.size[1]), 2)
    return surface

def save_colorbar(color_min, color_max, label : str = ""):
    global _fig



    _fig.clear()
    _ax = plt.axes((0, 0, 0.2, 1))
    #_ax = plt.axes((0, 0, 0.2, 1))  
    #_ax = plt.axes((0, 0, 0.2, 1))  
    #_ax = plt.axes((0, 0, 0.2, 1))
    #_fig.clear()
    # Create a ScalarMappable object to generate a colorbar
    norm = plt.Normalize(vmin=color_min, vmax=color_max)
    cmap = cm.viridis
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)


    # Add the colorbar to the figure
    bar = _fig.colorbar(sm, ax=_ax)
    bar.set_label(label=label, size=14, family='serif') #weight="bold"
    # Remove the axis (so only the colorbar is visible)
    #ax.set_axis_off()
    _ax.remove()


    # Create a BytesIO buffer to hold the image

    # Save the figure to the buffer instead of a file
    plt.savefig(f"_{label}_colorbar.jpg", format='jpg', bbox_inches='tight', pad_inches=0.05, transparent=True, dpi=600)



def draw_loop():
    while True:
        with open("_colorbar_settings.txt", "r") as cb_settings:
            json_string = cb_settings.readline().removesuffix("\n")
        try:
            settings = json.loads(json_string)
            color_min = settings["min"]
            color_max = settings["max"]
            label = settings["label"]
            save_colorbar(color_min, color_max, label)
        except:
            pass
        time.sleep(_delay)

if __name__ == "__main__":

    if sys.argv[1] == "loop":
        _delay = float(sys.argv[2])
        draw_loop()
    pygame.image.save(make_colorbar_surf(0, 20), "twenty.png")
    pygame.image.save(make_colorbar_surf(0, 1000), "thou.png")