import click
import os
import pathlib
import tempfile
import traceback
import requests
import pyfiglet
from duckduckgo_search import DDGS
from io import BytesIO
from PIL import Image


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
        try:
            # Create a temporary directory and file using pathlib.
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file_path = pathlib.Path(temp_dir) / "temp.jpg"
                with open(temp_file_path, "wb") as f:
                    image.save(f, "JPEG")
                # Lazy import ascii_magic only when needed.
                import ascii_magic
                art = ascii_magic.from_image(str(temp_file_path))
                art.to_terminal()
            click.echo("Rendering complete.")
        except Exception:
            click.echo("Error generating ASCII art:")
            traceback.print_exc()
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
        images_dir = pathlib.Path("images")
        images_dir.mkdir(exist_ok=True)
        sanitized_query = "".join(c if c.isalnum() or c in " _-" else "_" for c in description)
        image_path = images_dir / f"{sanitized_query}.jpg"
        try:
            image.save(str(image_path), "JPEG")
            click.echo(f"Image saved as '{image_path}'")
            # Open the image with the default viewer.
            Image.open(str(image_path)).show()
        except Exception:
            click.echo("Error saving or displaying image:")
            traceback.print_exc()
    else:
        click.echo("No image available for the query.")

if __name__ == "__main__":
    cli()
