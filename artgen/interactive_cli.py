# src/artgen/interactive.py

import os
import pathlib
import tempfile
from io import BytesIO

import requests
from PIL import Image, ImageEnhance
# import ascii_magic
from duckduckgo_search import DDGS

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import (
    Label,
    Button,
    Input,
    Checkbox,
    Log,
    LoadingIndicator
)
from textual.reactive import reactive

# For PDF output
from fpdf import FPDF

# Check if Pillow supports gamma
try:
    from PIL import ImageOps
    HAS_IMAGEOPS_GAMMA = True
except ImportError:
    HAS_IMAGEOPS_GAMMA = False


def fetch_image_from_internet(query: str):
    """
    Fetch a single image from DuckDuckGo. Returns PIL Image or None on failure.
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
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(image_url, headers=headers, timeout=15)
            resp.raise_for_status()
            return Image.open(BytesIO(resp.content))
    except Exception as e:
        print("Error fetching image from internet:", e)
    return None


class ArtGenTUI(App):
    """
    A Textual-based TUI for ArtGen, organized with vertical sections
    to better display controls and an export option, plus a Quit button.
    Compatible with Textual 2.1.x (no markup or wrap in Log).
    """

    CSS = """
    Screen {
        layout: vertical;
        padding: 1;
        align: center middle;
        overflow-x: auto;
    }

    #main-container {
        width: 45%;
        border: solid green;
        padding: 1 1 0 1;
    }

    #input_path {
        margin-right: 2;
    }

    #controls-container {
        width: 100%;
        border: round yellow;
        padding: 0 1 0 1;
    }

    #btn_local {
        margin-right: 1;
    }

    #btn_search {
        margin-left: 1;
    }

    #btn_save {
        margin-right: 1;
    }
    
    #btn_generate {
        margin-right: 2;
    }

    #btn_quit {
        margin-left: 60;
        width: 2%;
    }

    #title{
        margin-right: 5;
    }

    .filler {
        width: 50%;
    }

    .inline_lbl_btn {
        padding-top: 1;
        margin-right: 1;
    }

    /* Make inputs smaller so buttons fit on the same row */
    .small-input {
        width: 60;
    }
    .xsmall-input {
        width: 20;
    }

    /* Each row of controls */
    .controls-row {
        margin-bottom: 0; /* minimal vertical spacing between rows */
        width: 100%;
    }

    .title-row {
        height: 3; /* minimal vertical spacing between rows */
    }

    #preview-container {
        width: 45%;
        height: 10;
        border: round yellow;
        padding: 1;
    }

    #ascii_preview {
        height: 6; /* fixed height so it's scrollable if ASCII is long */
        overflow-y: auto;
    }

    /* Make the loading indicator smaller. */
    #loading_indicator {
        width: 20%;
        height: 2;
    }

    """

    current_image: reactive[Image.Image | None] = reactive(None)
    ascii_result: reactive[str | None] = reactive(None)

    def compose(self) -> ComposeResult:
        """
        Build the UI layout with a Horizontal split:
        - Left: controls (vertical sections)
        - Right: ASCII preview
        """
        with Container(id="main-container"):
            with Horizontal(classes="title-row"):
                yield Label("ArtGen Interactive Mode", id="title")
                yield LoadingIndicator(id="loading_indicator")
                yield Button("X", id="btn_quit")
            
            with Container(id="controls-container"):
                    
            # 1) Image source row
                with Horizontal(classes="controls-row"):
                    yield Label("Image Source:", classes="inline_lbl_btn")
                    yield Input(placeholder="Local path or search query", id="input_path", classes="small-input")

            # # Row 2: Buttons row: Load Local, Search Online, Grayscale            
                with Horizontal(classes="controls-row"):
                    yield Button("Load Local", id="btn_local")
                    yield Button("Search Online", id="btn_search")
                    yield Checkbox("Grayscale?", id="chk_grayscale")

            # 3) Generate ASCII row
                with Horizontal(classes="controls-row"):
                    yield Label("Generate ASCII:", classes="inline_lbl_btn")
                    yield Button("Generate", id="btn_generate")

            # 4) Export row
                with Horizontal(classes="controls-row"):
                    yield Label("Export ASCII as:", classes="inline_lbl_btn")
                    yield Input(value="html", id="input_format", classes="xsmall-input")  # default is html
                    yield Button("Save ASCII", id="btn_save")
                    yield Button("Save Image", id="btn_img_save")

        # Preview container at bottom
        with Container(id="preview-container"):
            yield Label("ASCII Preview:")
            yield Log(id="ascii_preview")  # Plain text only
            

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handle button presses by ID.
        """
        match event.button.id:
            case "btn_local":
                await self.load_local_image()
            case "btn_search":
                await self.search_online_image()
            case "btn_generate":
                await self.generate_ascii()
            case "btn_save":
                await self.save_output_to_file()
            case "btn_img_save":
                await self.save_img_to_file()
            case "btn_quit":
                # Exit the TUI immediately
                self.exit()

    async def load_local_image(self):
        """
        Load an image from a local path.
        """
        path_input = self.query_one("#input_path", Input).value.strip()
        log_widget = self.query_one("#ascii_preview", Log)

        if not os.path.isfile(path_input):
            log_widget.write("Local file not found!")
            return

        try:
            self.current_image = Image.open(path_input)
            log_widget.write(f"Loaded local image: {path_input}")
        except Exception as e:
            log_widget.write(f"Error loading image: {e}")

    async def search_online_image(self):
        """
        Fetch an image from DuckDuckGo.
        """
        query = self.query_one("#input_path", Input).value.strip()
        log_widget = self.query_one("#ascii_preview", Log)
        if not query:
            log_widget.write("Please enter a search query.")
            return

        loading = self.query_one("#loading_indicator", LoadingIndicator)
        loading.display = True
        self.refresh()  # synchronous in Textual 2.1.x

        try:
            img = fetch_image_from_internet(query)
            if img:
                self.current_image = img
                log_widget.write(f"Fetched image for query: '{query}'")
            else:
                log_widget.write("No image returned from DuckDuckGo.")
        finally:
            loading.display = False
            self.refresh()

    async def generate_ascii(self):
        """
        Process the image (resize, brightness, contrast, gamma, grayscale),
        then convert to ASCII using ascii_magic.
        """
        log_widget = self.query_one("#ascii_preview", Log)
        log_widget.clear()

        if not self.current_image:
            log_widget.write("No image loaded!")
            return

        width_str = "100"
        height_str = "80"
        brightness_str = "1.0"
        contrast_str = "1.0"
        gamma_str = "1.0"
        grayscale = self.query_one("#chk_grayscale", Checkbox).value

        def parse_float(s, default=1.0):
            try:
                return float(s)
            except ValueError:
                return default

        brightness = parse_float(brightness_str, 1.0)
        contrast = parse_float(contrast_str, 1.0)
        gamma = parse_float(gamma_str, 1.0)

        def parse_int(s):
            try:
                return int(s)
            except ValueError:
                return None

        target_width = parse_int(width_str)
        target_height = parse_int(height_str)

        img = self.current_image.copy()

        # Resize
        if target_width and target_height:
            img = img.resize((target_width, target_height))
        elif target_width or target_height:
            w, h = img.size
            if target_width and not target_height:
                ratio = target_width / float(w)
                new_h = int(h * ratio)
                img = img.resize((target_width, new_h))
            elif target_height and not target_width:
                ratio = target_height / float(h)
                new_w = int(w * ratio)
                img = img.resize((new_w, target_height))

        # Brightness
        if brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(brightness)

        # Contrast
        if contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(contrast)

        # Gamma
        if gamma != 1.0 and HAS_IMAGEOPS_GAMMA:
            from PIL import ImageOps
            img = ImageOps.gamma(img, gamma)
        elif gamma != 1.0:
            log_widget.write("Gamma not supported in this Pillow version.")

        # Grayscale
        if grayscale:
            img = img.convert("L")

        # Convert to ASCII
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = pathlib.Path(tmpdir) / "temp.jpg"
            img.save(temp_path, "JPEG")
            from ascii_magic import AsciiArt
            art = AsciiArt.from_image(str(temp_path))

        self.ascii_result = art
        log_widget.write("Rendering complete!")

    async def save_output_to_file(self):
        """
        Saves ASCII art to txt/html/pdf, depending on user input.
        """
        log_widget = self.query_one("#ascii_preview", Log)
        if not self.ascii_result:
            log_widget.write("No ASCII art to save! Generate first.")
            return

        fmt = self.query_one("#input_format", Input).value.strip().lower()
        if fmt == "html":
            filename = "artgen_output.html"
            # self._save_as_html(filename, self.ascii_result)
            self.ascii_result.to_html_file(filename, columns=200)
            log_widget.write(f"Saved HTML to: {filename}")
        elif fmt == "pdf":
            filename = "artgen_output.pdf"
            # self._save_as_pdf(filename, self.ascii_result)
            self.ascii_result.to_file(filename)
            log_widget.write(f"Saved PDF to: {filename}")
        else:
            filename = "artgen_output.txt"
            self.ascii_result.to_file(filename)
            log_widget.write(f"Saved text to: {filename}")

    async def save_img_to_file(self):
        """
        Saves image to current directory.
        """
        query = self.query_one("#input_path", Input).value.strip()
        log_widget = self.query_one("#ascii_preview", Log)
        if not self.current_image:
            log_widget.write("No image to save!")
            return

        filename = f"{query}.jpg"
        self.current_image.save(filename)
        log_widget.write(f"Saved image to: {filename}")
