import argparse
import os
import requests
import pyfiglet
import ascii_magic
# from ascii_magic import AsciiArt, Back
import tempfile
from duckduckgo_search import DDGS
from io import BytesIO
from PIL import Image

import sys
import traceback
import click

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
        traceback.print_exc()
    return None

@click.group()
def cli():
    """ArtGen CLI: Generate ASCII art or images based on a brief description."""
    pass

@cli.command("generate_art")
@click.argument("description")
def generate_art_cmd(description):
    """Generate ASCII art from an image."""
    click.echo(f"Attempting to fetch image for '{description}'...")
    image = fetch_image_object(description)
    if image:
        click.echo(f"Image fetched for '{description}'. Generating ASCII art...")
        fd, temp_path = tempfile.mkstemp(suffix=".jpg")
        try:
            with os.fdopen(fd, "wb") as tmp:
                image.save(tmp, "JPEG")
            art = ascii_magic.from_image(temp_path)
        except Exception as e:
            click.echo("Error generating ASCII art:")
            traceback.print_exc()
            art = None
        try:
            os.remove(temp_path)
        except Exception as e:
            click.echo("Error removing temporary file:")
            traceback.print_exc()
        if art:
            art.to_terminal()
            click.echo("Rendering complete.")
        else:
            click.echo(pyfiglet.figlet_format(description))
    else:
        click.echo("No image could be fetched. Falling back to pyfiglet stylized text.")
        click.echo(pyfiglet.figlet_format(description))

@cli.command("generate_word")
@click.argument("description")
def generate_word_cmd(description):
    """Generate stylized text using pyfiglet."""
    click.echo(pyfiglet.figlet_format(description))


@cli.command("generate_img")
@click.argument("description")
def generate_img_cmd(description):
    """Fetch and save an image locally."""
    click.echo(f"Attempting to fetch image for '{description}'...")
    image = fetch_image_object(description)
    if image:
        click.echo(f"Image fetched for '{description}'. Saving locally...")
        images_dir = "images"
        os.makedirs(images_dir, exist_ok=True)
        sanitized_query = "".join(c if c.isalnum() or c in " _-" else "_" for c in description)
        image_path = os.path.join(images_dir, f"{sanitized_query}.jpg")
        try:
            image.save(image_path, "JPEG")
            click.echo(f"Image saved as '{image_path}'")
            img = Image.open(image_path)
            img.show()
        except Exception as e:
            click.echo("Error saving or displaying image:")
            traceback.print_exc()
    else:
        click.echo("No image available for the query.")



# def main():
#     parser = argparse.ArgumentParser(
#         description="ArtGen CLI: Generate ASCII art based on a brief description."
#     )

#     subparsers = parser.add_subparsers(dest="command", required=True)

#     # Subcommand: generate_art
#     parser_art = subparsers.add_parser("generate_art", help="Generate ASCII art from an image.")
#     parser_art.add_argument("description", type=str, help="A brief description (preferably a single word)")

#     # Subcommand: generate_word
#     parser_word = subparsers.add_parser("generate_word", help="Generate stylized text using pyfiglet.")
#     parser_word.add_argument("description", type=str, help="A brief description")

#     # Subcommand: generate_img
#     parser_img = subparsers.add_parser("generate_img", help="Fetch and save an image locally.")
#     parser_img.add_argument("description", type=str, help="A brief description")

#     # parser.add_argument(
#     #     "command",
#     #     choices=["generate_art", "generate_word", "generate_img"],
#     #     help="Command to run: 'generate_art' for ASCII art, 'generate_word' for stylized text, 'generate_img' for image display."
#     # )
#     # parser.add_argument(
#     #     "description",
#     #     help="A brief description (preferably a single word for best results)"
#     # )

#     args = parser.parse_args()

#     if args.command == "generate_art":
#         generate_art(args.description)

#     elif args.command == "generate_word":
#         print(pyfiglet.figlet_format(args.description))

#     elif args.command == "generate_img":
#         print(generate_img(args.description))
#     else:
#         parser.print_help()
#         sys.exit(1)

if __name__ == "__main__":
    cli()
