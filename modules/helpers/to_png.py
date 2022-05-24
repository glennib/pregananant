from os import PathLike
from pathlib import Path
from PIL import Image
import io


def to_png(filename: PathLike):
    image = Image.open(filename)
    bytes = io.BytesIO()
    image.save(bytes, format="PNG")
    return bytes.getvalue()
