import argparse
import os
import requests
import pyfiglet
import ascii_magic
from ascii_magic import AsciiArt, Back
import tempfile
from duckduckgo_search import DDGS
from io import BytesIO
from PIL import Image


ASCII_CHARS = ['.',',',':',';','+','*','?','%','S','#','@']
ASCII_CHARS = ASCII_CHARS[::-1]

new_width=100

def get_ansi_color(value):
    r, g, b = value
    return '\x1b[38;2;{r};{g};{b}m'.format(r=str(r).zfill(3), g=str(g).zfill(3), b=str(b).zfill(3))

def grayscalify(image):
    return image.convert('L')

def modify(image_g, image, buckets=25):
    initial_pixels_g = list(image_g.getdata())
    initial_pixels = list(image.getdata())

    new_pixels = [get_ansi_color(initial_pixels[i]) + ASCII_CHARS[pixel_value//buckets] for i, pixel_value in enumerate(initial_pixels_g)]
    return ''.join(new_pixels)

def fetch_image_object(query):
    """
    Dynamically fetch an image for the given query using DuckDuckGo search.
    Returns a PIL Image object loaded from an in-memory byte stream.
    """
    try:
        results = DDGS().images(
            keywords=query,
            region="wt-wt",
            safesearch="moderate",
            max_results=1
        )
        if results:
            image_url = results[0]["image"]
            # Mimic a browser with a User-Agent header to avoid 403 errors.
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/114.0.0.0 Safari/537.36"
                )
            }
            response = requests.get(image_url, headers=headers)
            response.raise_for_status()
            image_data = response.content
            image = Image.open(BytesIO(image_data))
            return image
    except Exception as e:
        print("Error fetching image:", e)
    return None

def generate_art(query):
    """
    Generate ASCII art for the given query by:
      1. Dynamically fetching an image using DuckDuckGo search.
      2. Saving the in-memory image to a temporary file.
      3. Converting the image to ASCII art with ascii_magic.
      4. Falling back to pyfiglet for stylized text if no image is available.
    """
    print(f"Attempting to fetch image for '{query}'...")
    image = fetch_image_object(query)
    if image:
        print(f"Image fetched for '{query}'. Generating ASCII art...")
        # Use tempfile.mkstemp to get a file descriptor and path, then write and close the file.
        fd, temp_path = tempfile.mkstemp(suffix=".jpg")
        try:
            with os.fdopen(fd, "wb") as tmp:
                image.save(tmp, format="JPEG")
            # Now the file is closed; generate ASCII art from its path.
            art = ascii_magic.from_image(temp_path)
            # art = AsciiArt.from_image(temp_path)
            # my_output = art.to_ascii(columns=100, back=Back.BLUE)
            # print(my_output)
        except Exception as e:
            print("Error generating ASCII art:", e)
            art = None
        # Try to remove the temporary file.
        try:
            os.remove(temp_path)
        except Exception as e:
            print("Error removing temporary file:", e)
        # Display the ASCII art if generation succeeded.
        if art:
            art.to_terminal()
            print("Rendering..")
        else:
            print(pyfiglet.figlet_format(query))
    else:
        print("No image could be fetched. Falling back to pyfiglet stylized text.")
        print(pyfiglet.figlet_format(query))

def generate_local_art(query):
    """
    Generate ASCII art for the given query using a local image file.
    """
    print(f"Attempting to fetch image for '{query}'...")
    image = fetch_image_object(query)
    if image:
        print(f"Image fetched for '{query}'. Generating ASCII art...")
        # Use tempfile.mkstemp to get a file descriptor and path, then write and close the file.
        # fd, temp_path = tempfile.mkstemp(suffix=".jpg")
        # try:
        #     with os.fdopen(fd, "wb") as tmp:
        #         image.save(tmp, format="JPEG")
        image_g = grayscalify(image)

        pixels = modify(image_g, image)

        len_pixels = len(pixels)

        pixel_size = 1 + len(get_ansi_color((255,255,255)))

        # Construct the image from the character list
        new_image = [pixels[index:index+new_width*pixel_size] for index in range(0, len_pixels, new_width*pixel_size)]

        return '\n'.join(new_image)
    return "No image could be fetched locally. Please try again with a different query."



def main():
    parser = argparse.ArgumentParser(
        description="ArtGen CLI: Generate ASCII art based on a brief description."
    )
    parser.add_argument(
        "command",
        choices=["generate"],
        help="Command to run (only 'generate' is supported)"
    )
    parser.add_argument(
        "description",
        help="A brief description (preferably a single word for best results)"
    )
    args = parser.parse_args()

    if args.command == "generate":
        generate_art(args.description)

    # if args.command == "generate_local":
    #     print(generate_local_art(args.description))

if __name__ == "__main__":
    main()
