#!/usr/bin/env python3

import datetime
import io
from os import PathLike
import pathlib as pl
from typing import Any, Dict, List, Optional
from pathlib import Path
import PySimpleGUI as sg
import pandas as pd
import json
import helpers
from pprint import pformat, pprint

METADATA_PATH = Path("./metadata.json")
IMG_DIR = pl.Path("./imgs")


def image_files(dir: Path) -> List[Path]:
    filenames = [
        f
        for f in dir.iterdir()
        if f.is_file() and f.suffix.lower().endswith((".png", ".jpeg", ".jpg"))
    ]
    return filenames


def populate_annotations(annotations, filenames: List[Path]):
    for f in filenames:
        # Check if filename exists in the annotations list
        annotation: Optional[Dict] = next(
            (
                a
                for a in annotations
                if "filename" in a and a["filename"] == f.as_posix()
            ),
            None,
        )
        # If it isn't, create an entry
        if annotation is None:
            annotation = {
                "filename": f.as_posix(),
            }
            annotations.append(annotation)
        if "included" not in annotation:
            annotation["included"] = True


def get_headers(annotations: List[Dict]):
    headers = set()
    for a in annotations:
        headers.update(a.keys())
    return list(headers)


def load(path: Path) -> Dict[str, Any]:
    if not path.exists():
        with path.open("w+") as f:
            json.dump({}, f)
    with path.open("r") as f:
        try:
            meta = json.load(f)
        except json.JSONDecodeError:
            meta = {}
    return meta


def dump(meta: Dict[str, Any], path: Path):
    with path.open("w") as f:
        json.dump(meta, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    meta = load(METADATA_PATH)

    if "annotations" not in meta:
        meta["annotations"] = []
    annotations: List[Dict[str, Any]] = meta["annotations"]

    filenames = image_files(IMG_DIR)
    populate_annotations(annotations, filenames)

    dump(meta, METADATA_PATH)

    # headers = get_headers(annotations)
    table = pd.DataFrame(annotations)
    table_headers = list(table.columns)
    table_values = table.values.tolist()
    # pprint(table_values)

    pprint(table_headers)

    # exit(0)

    # print(table)

    selection_column = []

    for annotation in annotations:
        fn: PathLike = annotation["filename"]
        exif = helpers.get_exif(fn)
        selection_column.append(
            [
                sg.Checkbox(fn),
            ]
        )
        if "DateTime" in exif:
            dt: datetime.datetime = exif["DateTime"]
        else:
            print(f"{fn} didn't have exif data DateTime, printing it all:")
            pprint(exif)
            continue
        week = dt.isocalendar()[1]
        print(f"{fn}: {week}")

    layout = [[sg.Column(selection_column)]]

    window = sg.Window("Image Viewer", layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

    dump(meta, METADATA_PATH)
