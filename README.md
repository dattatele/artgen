## ArtGen

ArtGen is a CLI tool that generates ASCII art from images and text. This project was created out of an interest in building something fun using existing Python packages. It is free, open-source, and designed to convert images into ASCII art. Additional features and changes are being explored and will be updated in upcoming versions.

## Features

Two New features
- **interactive web** mode to allow more control and support for local image upload
- **interactive cli** mode to allow run within terminal.

- Fetches images using DuckDuckGo
- Converts images to ASCII art
- Shows fallback stylized text with `pyfiglet`

## Installation

You can install ArtGen from [PyPI](https://pypi.org):

```bash
  pip install artgen --upgrade
```

## Usage

To generate ASCII art, use the following command:

```bash

  artgen generate_art "Cat"

  artgen generate_word "Sunflower"

  artgen generate_img "ASCII"

```

### For interactive

For web interface:
```bash
   artgen interactive

```
That will open on [localhost or ](http://localhost:5000/)

For cli interactive interface:
```bash
   artgen interactive_cli
```

That will launch in terminal. Known issue for terminal mode for some windows user had permission issue saving file but works on linux or osx


## Contributing

Contributions are welcome! Please open an issue or PR on GitHub.

