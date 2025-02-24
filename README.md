## ArtGen 🎨🚀 [![PyPI](https://img.shields.io/pypi/v/artgen.svg)](https://pypi.org/project/artgen/) 

![image](https://github.com/user-attachments/assets/b451d09f-c1e6-4f7f-8ab8-d8802571b2f4) 

ArtGen is a CLI tool that generates ASCII art from images and text. This project was created out of an interest in building something fun using existing Python packages. It is free, open-source, and designed to convert images into ASCII art. Additional features and changes are being explored and will be updated in upcoming versions.

## Features

Two New features
- **interactive web** mode to allow more control and support for local image upload
- **interactive cli** mode to allow run within terminal.

- Fetches images using DuckDuckGo
- Converts images to ASCII art
- Shows fallback stylized text with `pyfiglet`

## Installation

**Make sure you have python 3.12 or higher** installed. You can download and install directly from python [official](https://www.python.org/)  

You can install ArtGen from [PyPi](https://pypi.org/project/artgen/): 

```bash
  pip install artgen --upgrade
```

## Usage

### For interactive

For web interface:
```bash
   artgen interactive

```
That will open on [localhost or ](http://localhost:5000/)
![image](https://github.com/user-attachments/assets/c60d4083-e8ee-46fd-a5df-a0be11aa39c0)


For cli interactive interface:
```bash
   artgen interactive_cli
```
![image](https://github.com/user-attachments/assets/f8ea870b-399c-454d-baf5-a01b84e1d89a)


### Just running in CMD:

To generate ASCII art, use the following command:

```bash

  artgen generate_art "Cat"

  artgen generate_word "Sunflower"

  artgen generate_img "ASCII"

```
![image](https://github.com/user-attachments/assets/4397b5c9-2058-46e7-a5ab-c18318eaeb8d)


```bash
  artgen generate_art "frenchie"

```

![image](https://github.com/user-attachments/assets/408af775-5883-488e-ae55-bae0371432ca)

## Contributing

Contributions are welcome! Please open an issue or PR on GitHub.

