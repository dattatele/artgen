import click
import pathlib
import tempfile
import traceback
import pyfiglet
from PIL import Image

from artgen.img import fetch_image_object
from artgen.interactive_cli import ArtGenTUI
from artgen.interactive_web import app

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


@cli.command("interactive_cli")
def interactive_cmd():
    """Launch the new Textual TUI for advanced usage."""
    ArtGenTUI().run()


@cli.command("interactive")
@click.option("--host", default="127.0.0.1", help="Host to run the web server on")
@click.option("--port", default=5000, help="Port to run the web server on")
def interactive_web_cmd(host, port):
    """Launch the browser-based interactive mode."""
    click.echo(f"Starting ArtGen Web Interactive at http://{host}:{port}")
    app.run(host=host, port=port)


if __name__ == "__main__":
    cli()
