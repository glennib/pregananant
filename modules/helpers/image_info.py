from os import PathLike
from PIL import Image, ImageOps

def normalized(filename: PathLike) -> Image:
    im = Image.open(filename)
    return ImageOps.exif_transpose(im)


def get_layout(filename: PathLike) -> str:
    im = normalized(filename)
    width, height = im.size
    if width > height:
        return "landscape"
    else:
        return "portrait"
