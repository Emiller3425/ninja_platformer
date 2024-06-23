from PIL import Image
import os

# Directory containing the PNG files
directory = '../graphics/spritesheet_images'

# Path to the tilesheet file
tilesheet_path = os.path.join(directory, 'tilesheet.png')

# Remove the existing tilesheet file if it exists
if os.path.exists(tilesheet_path):
    os.remove(tilesheet_path)

# List all PNG files in the directory
files = [f for f in os.listdir(directory) if f.endswith('.png')]

# Sort the files to ensure consistent order
files.sort()

# Open all images and store them in a list
images = [Image.open(os.path.join(directory, file)) for file in files]

# Set the size of each tile
tile_width, tile_height = 16, 16

# Calculate the total number of tiles across all images
num_tiles = sum((image.width // tile_width) * (image.height // tile_height) for image in images)

# Determine the size of the tilesheet
tiles_per_row = 10  # Adjust based on your preference
tilesheet_width = tile_width * tiles_per_row
tilesheet_height = tile_height * ((num_tiles + tiles_per_row - 1) // tiles_per_row)

# Create a blank image for the tilesheet
tilesheet = Image.new('RGBA', (tilesheet_width, tilesheet_height))

# Paste each 16x16 section into the tilesheet
tile_index = 0
for image in images:
    image_width, image_height = image.size
    for y in range(0, image_height, tile_height):
        for x in range(0, image_width, tile_width):
            tile = image.crop((x, y, x + tile_width, y + tile_height))
            ts_x = (tile_index % tiles_per_row) * tile_width
            ts_y = (tile_index // tiles_per_row) * tile_height
            tilesheet.paste(tile, (ts_x, ts_y))
            tile_index += 1

# Save the tilesheet
tilesheet.save('tilesheet.png')