#!/usr/bin/env python3

import datetime
import io
from os import PathLike
import pathlib as pl
from re import S
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import PySimpleGUI as sg
import pandas as pd
import json
import helpers
from pprint import pformat, pprint

from helpers.to_png import to_png

METADATA_PATH = Path("./metadata.json")
IMG_DIR = pl.Path("./imgs")
START_DATE = datetime.datetime(2021, 10, 15)
DATETIME_FORMAT_STRING = "%Y-%m-%d %H:%M:%S"
JPEG_SUFFIXES = (".jpg", ".jpeg")


def image_files(dir: Path) -> List[Path]:
    filenames = [
        f
        for f in dir.iterdir()
        if f.is_file() and f.suffix.lower().endswith((".png", ".jpeg", ".jpg"))
    ]
    return filenames


def sort_annotations(annotations: List[Dict[str, Any]], key: str):
    annotations.sort(key=lambda it: it[key])


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

        if "datetime" not in annotation:
            exif = helpers.get_exif(f)
            if "DateTime" in exif:
                dt: datetime.datetime = exif["DateTime"]
                annotation["datetime"] = dt.strftime(DATETIME_FORMAT_STRING)
            else:
                print(f"{fn} didn't have exif data DateTime, printing it all:")
                pprint(exif)

        if "pregnancy_week" not in annotation:
            dt = datetime.datetime.fromisoformat(annotation["datetime"])
            diff = dt - START_DATE
            pregnancy_week = diff.days // 7
            annotation["pregnancy_week"] = pregnancy_week
    sort_annotations(annotations, "datetime")


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


def get_suffix(s: str) -> int:
    assert "_" in s
    i = s.rfind("_")
    return int(s[i + 1 :])


if __name__ == "__main__":
    meta = load(METADATA_PATH)

    if "annotations" not in meta:
        meta["annotations"] = []
    annotations: List[Dict[str, Any]] = meta["annotations"]

    filenames = image_files(IMG_DIR)
    populate_annotations(annotations, filenames)

    dump(meta, METADATA_PATH)

    selection_column = []
    radio_default = True

    for i, annotation in enumerate(annotations):
        fn: PathLike = annotation["filename"]
        selection_column.append(
            [
                sg.Checkbox(
                    "",
                    default=annotation.get("included", True),
                    key=f"included_{i}",
                    enable_events=True,
                ),
                sg.Radio(
                    f"{annotation['pregnancy_week']:2}",
                    key=f"radio_{i}",
                    group_id="radio_view",
                    default=radio_default,
                    enable_events=True,
                ),
            ]
        )
        radio_default = False

    viewer_column = [[sg.Text("", key="filename")], [sg.Image(key="image", size=(512, 512))]]

    layout = [
        [
            sg.Column(selection_column, scrollable=True),
            sg.VSeparator(),
            sg.Column(viewer_column),
        ],
    ]

    window = sg.Window("Image Viewer", layout, size=(1024, 1024), resizable=True)

    image_viewer = window["image"]

    while True:
        event: str
        values: Dict[str, Any]
        event, values = window.read()
        if event is sg.WIN_CLOSED or event == "Exit":
            break
        if event.startswith("included_"):
            assert isinstance(values[event], bool)
            i = get_suffix(event)
            annotation = annotations[i]
            annotation["included"] = values[event]
        if event.startswith("radio_"):
            assert isinstance(values[event], bool)
            assert values[event]
            i = get_suffix(event)
            annotation = annotations[i]
            filename = annotation["filename"]
            if filename.lower().endswith(JPEG_SUFFIXES):
                img = to_png(filename)
                image_viewer.update(data=img)
            else:
                image_viewer.update(filename=filename, size=(512, 512))

    dump(meta, METADATA_PATH)
