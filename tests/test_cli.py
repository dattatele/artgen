import os
import pathlib
import pytest
import pyfiglet
from PIL import Image
from click.testing import CliRunner

# Import from your package
from artgen.cli import cli, fetch_image_object

"""
This file contains both:
  - Unit tests (with monkeypatch) that do NOT hit the network (stable tests).
  - Integration tests (real network calls) that DO fetch from DuckDuckGo.
"""

#
# ──────────────────────────────────────────────────────────────
#  1. TESTS FOR generate_word (No mocking needed)
# ──────────────────────────────────────────────────────────────
#

def test_generate_word():
    """
    Checks that the output of 'generate_word' matches pyfiglet's exact output 
    for the same string. This ensures coverage of the pyfiglet path.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["generate_word", "sunflower"])
    assert result.exit_code == 0

    expected = pyfiglet.figlet_format("sunflower")
    # Compare stripped lines to avoid trailing newlines mismatches
    assert result.output.strip() == expected.strip()


#
# ──────────────────────────────────────────────────────────────
#  2. UNIT TESTS FOR generate_art (Mocked fetch_image_object)
# ──────────────────────────────────────────────────────────────
#

def fake_image_success(_query):
    """
    Return a dummy white 10x10 image to simulate a successful fetch.
    This ensures we avoid actual network calls in this test.
    """
    return Image.new("RGB", (10, 10), "white")

def test_generate_art_success_unit(monkeypatch):
    """
    Unit test for generate_art: 
      - We mock fetch_image_object to return a dummy image.
      - Ensures we don't rely on a real network call.
    """
    monkeypatch.setattr("artgen.cli.fetch_image_object", fake_image_success)

    runner = CliRunner()
    result = runner.invoke(cli, ["generate_art", "sunflower"])
    assert result.exit_code == 0
    # 'Rendering complete.' implies ascii_magic succeeded
    assert "Rendering complete." in result.output
    # Ensure fallback text isn't used
    assert "Falling back" not in result.output

def test_generate_art_failure_unit(monkeypatch):
    """
    Unit test for generate_art:
      - We mock fetch_image_object to return None (simulating a failed fetch).
      - Code should fall back to pyfiglet.
    """
    monkeypatch.setattr("artgen.cli.fetch_image_object", lambda q: None)

    runner = CliRunner()
    result = runner.invoke(cli, ["generate_art", "sunflower"])
    assert result.exit_code == 0

    # The fallback output should match pyfiglet
    expected = pyfiglet.figlet_format("sunflower")
    assert expected.strip() in result.output.strip()


#
# ──────────────────────────────────────────────────────────────
#  3. UNIT TESTS FOR generate_img (Mocked fetch_image_object)
# ──────────────────────────────────────────────────────────────
#

def test_generate_img_success_unit(monkeypatch):
    """
    Unit test for generate_img:
      - Mocks image fetch with a dummy image
      - Verifies creation of images/ subdir & the saved file
    """
    monkeypatch.setattr("artgen.cli.fetch_image_object", fake_image_success)

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["generate_img", "sunflower"])
        assert result.exit_code == 0
        assert "Image saved as" in result.output

        images_dir = pathlib.Path("images")
        assert images_dir.exists()
        saved_files = list(images_dir.iterdir())
        assert len(saved_files) == 1
        assert "sunflower" in saved_files[0].name

def test_generate_img_failure_unit(monkeypatch):
    """
    Unit test for generate_img:
      - Mocks fetch_image_object to return None
      - Checks that we get a 'No image available' message
    """
    monkeypatch.setattr("artgen.cli.fetch_image_object", lambda q: None)

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["generate_img", "sunflower"])
        assert result.exit_code == 0
        assert "No image available" in result.output


#
# ──────────────────────────────────────────────────────────────
#  4. INTEGRATION TESTS (Real network calls to DuckDuckGo)
#     WARNING: May fail if offline or if DuckDuckGo changes results
# ──────────────────────────────────────────────────────────────
#

@pytest.mark.integration
def test_fetch_image_object_integration():
    """
    This integration test calls the real DDGS API to fetch an image for 'sunflower'.
    May fail if offline or if the API changes. 
    """
    image = fetch_image_object("sunflower")
    assert image is not None, "Expected to fetch a real image but got None"

@pytest.mark.integration
def test_generate_art_integration():
    """
    Integration test for generate_art with a real fetch for 'sunflower'.
    Checks if we can actually generate ASCII art from a real network call.
    """
    runner = CliRunner()
    result = runner.invoke(cli, ["generate_art", "sunflower"])
    # Could fail if no network or if DuckDuckGo doesn't return a valid image
    assert result.exit_code == 0
    # If an image was fetched & ascii_magic succeeded, we see "Rendering complete."
    # If something fails, code falls back to pyfiglet. Either way, it shouldn't crash.
    assert "Rendering complete." in result.output or "Falling back" in result.output

@pytest.mark.integration
def test_generate_img_integration():
    """
    Integration test for generate_img with a real fetch for 'sunflower'.
    Checks if an 'images' folder is created with the saved image.
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["generate_img", "sunflower"])
        assert result.exit_code == 0
        # We either see 'Image saved as...' or 'No image available...'
        # if the fetch fails.
        if "Image saved as" in result.output:
            images_dir = pathlib.Path("images")
            assert images_dir.exists()
            assert any("sunflower" in p.name for p in images_dir.iterdir())
        else:
            assert "No image available" in result.output
