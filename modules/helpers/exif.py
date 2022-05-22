from typing import Dict
from PIL import Image
from PIL.ExifTags import TAGS
from os import PathLike
import datetime as dt


def get_exif(filename: PathLike) -> Dict:
    image = Image.open(filename)
    exif_data = image.getexif()
    out = {}
    for tag_id in exif_data:
        tag = TAGS.get(tag_id, tag_id)
        data = exif_data.get(tag_id)

        if isinstance(data, bytes):
            data = data.decode()

        if isinstance(tag, str) and tag == "DateTime":
            date_str = data[:10]
            time_str = data[11:]
            year, month, day = map(int, date_str.split(":"))
            hour, minute, sec = map(int, time_str.split(":"))
            data = dt.datetime(year, month, day, hour, minute, sec)

        out[tag] = data
    return out
