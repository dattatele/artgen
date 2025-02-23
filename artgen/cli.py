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

import traceback
import click


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

if __name__ == "__main__":
    cli()
