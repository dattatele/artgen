# ArtGen

ArtGen is a command-line tool for generating ASCII art based on a brief description. Whether you input "rocket", "cat", or any phrase (up to 5 words), ArtGen will either display a pre-defined art template (if available) or dynamically construct an ASCII art banner.

## Features

- **Dynamic ASCII Generation:** Constructs an ASCII art frame based on your description.
- **Pre-defined Templates:** Provides built-in templates for keywords like `cat`, `dog`, `tree`, and `hello`.
- **Command-Line Interface:** Easily generate art using a simple CLI command.

## Installation

You can install ArtGen from [PyPI](https://pypi.org):

```bash
pip install artgen
```
Alternatively, if you're developing or testing locally, clone the repository and install in editable mode:

git clone https://github.com/yourusername/artgen.git
cd artgen
pip install -e .

Usage

To generate ASCII art, use the following command:

artgen generate_art "your description here"

artgen generate_word "your description here"

artgen generate_img "your description here"

For example:

artgen generate rocket

This will output a constructed ASCII art banner based on the description "rocket".