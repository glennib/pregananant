#!/usr/bin/env python3

from pathlib import Path
from typing import Dict, List, Any
from helpers import load, normalized
from pprint import pprint
from PIL import Image, ImageFont, ImageDraw

METADATA_PATH = Path("./metadata.json")
OUT_DIR = Path("./edited_imgs")


def is_empty(dir: Path):
    assert dir.exists()
    return not any(dir.iterdir())


def by_week(annotations_in: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    out: Dict[int, List[Dict[str, Any]]] = {}
    for annotation in annotations_in:
        week: int = annotation["pregnancy_week"]
        if week not in out:
            out[week]: List[Dict[str, Any]] = []
        out[week].append(annotation)
    for week, annotations in out.items():
        annotations.sort(key=lambda annotation: annotation["datetime"])

    return out


def filename(annotation: Dict[str, Any], image_number_in_week: int) -> str:
    week = annotation["pregnancy_week"]
    original_path = Path(annotation["filename"])
    suffix = original_path.suffix
    return f"{week:02}-{image_number_in_week:02}{suffix}"


def create_image(annotation: Dict[str, Any], dir: Path, image_number_in_week: int):
    original_path = Path(annotation["filename"])
    target_path = dir / filename(annotation, image_number_in_week)
    week = annotation["pregnancy_week"]

    print(f"processing {target_path}")

    image = normalized(original_path)
    size = 500
    font = ImageFont.truetype("OpenSans-Regular.ttf", size)
    drawable = ImageDraw.Draw(image)
    text = f"{week:2}"
    drawable.text(
        from_ratio(0.5, 0.0, image),
        text,
        fill=(255, 255, 255),
        stroke_width=10,
        stroke_fill=(0, 0, 0),
        font=font,
        anchor="ma",
    )
    image.save(target_path)


def delete_all_files(dir: Path):
    for file in dir.iterdir():
        if file.is_file():
            file.unlink()


def from_ratio(r_width: float, r_height: float, image: Image.Image):
    width, height = image.size
    p_width = int(round(r_width * width))
    p_height = int(round(r_height * height))
    return p_width, p_height


def main():
    if OUT_DIR.exists():
        assert OUT_DIR.is_dir()
    else:
        OUT_DIR.mkdir()

    if not is_empty(OUT_DIR):
        print(f"Deleting all files in {OUT_DIR}")
        delete_all_files(OUT_DIR)
        assert is_empty(OUT_DIR)

    meta = load(METADATA_PATH)
    annotations_by_week = by_week(meta["annotations"])

    for week, annotations in annotations_by_week.items():
        for image_number, annotation in enumerate(annotations, 1):
            create_image(annotation, OUT_DIR, image_number)
            #break
        #break


if __name__ == "__main__":
    main()
