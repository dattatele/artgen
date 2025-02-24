# src/artgen/interactive_web.py

import os
import io
import uuid
import tempfile
import pathlib
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.utils import secure_filename
import requests
from PIL import Image, ImageEnhance, ImageOps
from ascii_magic import AsciiArt 
from duckduckgo_search import DDGS

# Create Flask app
app = Flask(__name__)
app.secret_key = "replace_with_a_secure_secret"

# Configure upload folder
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# In-memory map of ascii_key -> ascii_html
ascii_map = {}

def fetch_image_from_internet(query: str):
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
            return Image.open(io.BytesIO(resp.content))
    except Exception as e:
        print("Error fetching image:", e)
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    # Process form submission
    if request.method == "POST":
        action = request.form.get("action")
        if action == "upload":
            # Local image upload
            if "local_image" not in request.files:
                flash("No file part in upload form.")
                # return redirect(request.url)
                return redirect(url_for("index"))
            file = request.files["local_image"]
            if file.filename == "":
                flash("No selected file")
                # return redirect(request.url)
                return redirect(url_for("index"))
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                session["current_image"] = filename  # store filename only
                # Clear old ASCII key if any
                old_key = session.pop("ascii_key", None)
                if old_key and old_key in ascii_map:
                    del ascii_map[old_key]
                flash(f"Uploaded local image: {filename}")
                return redirect(url_for("index"))
            else:
                flash("File type not allowed.")
                return redirect(url_for("index"))

        elif action == "search":
            # Online search
            query = request.form.get("search_query", "").strip()
            if not query:
                flash("Search query is empty!")
                return redirect(url_for("index"))
            img = fetch_image_from_internet(query)
            if img:
                # Save the fetched image to disk
                filename = secure_filename(query + ".jpg")
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                img.save(filepath, "JPEG")
                session["current_image"] = filename
                # Clear old ASCII key if any
                old_key = session.pop("ascii_key", None)
                if old_key and old_key in ascii_map:
                    del ascii_map[old_key]
                flash(f"Fetched image for query: '{query}'")
            else:
                flash("No image returned from DuckDuckGo.")
            return redirect(url_for("index"))
        

        elif action == "generate":
            # Generate ASCII art with processing parameters
            current_image = session.get("current_image")
            if not current_image:
                flash("No image loaded!")
                return redirect(url_for("index"))
            
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], current_image)
            try:
                img = Image.open(filepath)
            except Exception as e:
                flash(f"Error opening image: {e}")
                return redirect(url_for("index"))
            
            # Retrieve parameters
            try:
                brightness = float(request.form.get("brightness", 1.0))
            except:
                brightness = 1.0
            try:
                contrast = float(request.form.get("contrast", 1.0))
            except:
                contrast = 1.0
            try:
                gamma = float(request.form.get("gamma", 1.0))
            except:
                gamma = 1.0
            resolution = request.form.get("resolution", "medium")
            grayscale = request.form.get("grayscale") == "on"

            columns = int(request.form.get("columns", 200))
            color_mode = (request.form.get("color_mode") == "on")
            font_size = int(request.form.get("font_size", 14)) 

            # Preset resolutions
            presets = {
                "small": (100, 100),
                "medium": (200, 200),
                "large": (400, 400)
            }
            if resolution in presets:
                img = img.resize(presets[resolution])

            # Apply enhancements
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)
            if gamma != 1.0:
                try:
                    img = ImageOps.gamma(img, gamma)
                except Exception as e:
                    flash("Gamma adjustment not supported: " + str(e))

            if grayscale:
                img = img.convert("L")

            # Convert to ASCII
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_path = pathlib.Path(tmpdir) / "temp.jpg"
                img.save(temp_path, "JPEG")
                # Use AsciiArt.from_image() and then to_html() with a desired column width.
                art_obj = AsciiArt.from_image(str(temp_path))
                # You can adjust the number of columns (e.g., 200) as needed.
                # color= color_mode for enabling color
                ascii_html = art_obj.to_html(
                    columns=columns,
                    full_color=color_mode
                )


            # We embed the font-size in a wrapper <div> style
            # This avoids user losing color HTML markup
            ascii_html_wrapped = f'<div style="font-size: {font_size}px; line-height: {font_size}px;">{ascii_html}</div>'

            # Create new ascii_key
            new_key = str(uuid.uuid4())
            ascii_map[new_key] = ascii_html_wrapped
            # Remove old ascii_key
            old_key = session.pop("ascii_key", None)
            if old_key and old_key in ascii_map:
                del ascii_map[old_key]
            session["ascii_key"] = new_key

            flash("ASCII art generated!")
            return redirect(url_for("index"))
        

    # For export, we handle that with a separate route
    # GET request: render the page
    current_image = session.get("current_image")
    ascii_key = session.get("ascii_key")
    ascii_art = ascii_map.get(ascii_key, None)

    return render_template(
        "index.html",
        current_image=current_image,
        ascii_art=ascii_art
    )

@app.route("/export", methods=["GET"])
def export_ascii():
    ascii_key = session.get("ascii_key")
    ascii_art = session.get("ascii_art")
    if not ascii_art:
        flash("No ASCII art available to export!")
        return redirect(url_for("index"))
    
    fmt = request.args.get("fmt", "txt").lower()
    if fmt == "html":
        return send_file(
            io.BytesIO(ascii_art.encode("utf-8")),
            as_attachment=True,
            download_name="artgen_output.html",
            mimetype="text/html"
        )
    else:
        return send_file(
            io.BytesIO(ascii_art.encode("utf-8")),
            as_attachment=True,
            download_name="artgen_output.txt",
            mimetype="text/plain"
        )

if __name__ == "__main__":
    app.run(debug=True)

