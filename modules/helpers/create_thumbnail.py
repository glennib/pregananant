from os import PathLike
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageOps


def create_thumbnail(
    original_file: PathLike,
    *,
    size: Tuple[int, int],
    target_file: Optional[PathLike] = None
) -> PathLike:
    original_file = Path(original_file)
    assert original_file.exists()
    assert original_file.is_file()
    if target_file is None:
        target_file = original_file.with_suffix(original_file.suffix + ".thumbnail")
    target_file = Path(target_file)
    assert target_file != original_file

    im = Image.open(original_file)
    im = ImageOps.exif_transpose(im)
    im.thumbnail(size)
    im.save(target_file, "jpeg")
    return target_file
