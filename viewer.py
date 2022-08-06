#!/usr/bin/env python3

import datetime
import io
from os import PathLike
from re import S
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import PySimpleGUI as sg
import pandas as pd
import json
import helpers
from pprint import pformat, pprint
from helpers.create_thumbnail import create_thumbnail

from helpers.to_png import to_png

METADATA_PATH = Path("./metadata.json")
IMG_DIR = Path("./imgs")
THUMB_DIR = IMG_DIR / "thumb"
EXPECTED_END_DATE = datetime.datetime(2022, 8, 1)
EXPECTED_DURATION = datetime.timedelta(weeks=40, days=3)
START_DATE = EXPECTED_END_DATE - EXPECTED_DURATION
DATETIME_FORMAT_STRING = "%Y-%m-%d %H:%M:%S"
JPEG_SUFFIXES = (".jpg", ".jpeg")
ADJUST_TO_WEEKDAY = 0


def weekday(date: Union[datetime.datetime, str]) -> str:
    if isinstance(date, str):
        date = datetime.datetime.fromisoformat(date)
    return [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ][date.weekday()]


def image_files(dir: Path) -> List[Path]:
    filenames = [
        f
        for f in dir.iterdir()
        if f.is_file() and f.suffix.lower().endswith((".png", ".jpeg", ".jpg"))
    ]
    return filenames


def sort_annotations(annotations: List[Dict[str, Any]], key: str):
    annotations.sort(key=lambda it: it[key])


def closest_week(
    dt: datetime.datetime, start_date: datetime.datetime, adjust_to_weekday: int
) -> int:
    if dt.weekday() != adjust_to_weekday:
        days1 = (adjust_to_weekday - dt.weekday()) % 7
        dt1 = dt + datetime.timedelta(days=days1)
        days2 = (dt.weekday() - adjust_to_weekday) % 7
        dt2 = dt - datetime.timedelta(days=days2)
        diff1 = abs((dt1 - dt).total_seconds())
        diff2 = abs((dt2 - dt).total_seconds())
        if diff1 < diff2:
            dt = dt1
        else:
            dt = dt2
    diff = dt - start_date
    float_week = diff.days / 7.0
    week = round(float_week, 0)
    return int(week)


def populate_annotations(annotations: List[Dict[str, Any]], filenames: List[Path]):
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
                print(f"{f} didn't have exif data DateTime, printing it all:")
                pprint(exif)

        if "pregnancy_week" not in annotation:
            dt = datetime.datetime.fromisoformat(annotation["datetime"])
            pregnancy_week = closest_week(
                dt, START_DATE, adjust_to_weekday=ADJUST_TO_WEEKDAY
            )
            annotation["pregnancy_week"] = pregnancy_week

        if "layout" not in annotation or annotation["layout"] is None:
            annotation["layout"] = helpers.get_layout(f)

    sort_annotations(annotations, "datetime")


def create_thumbnails(annotations: List[Dict[str, Any]], thumb_dir: Path):
    thumb_dir.mkdir(parents=True, exist_ok=True)
    for annotation in annotations:
        original_img_path = Path(annotation["filename"])
        thumb_path = (thumb_dir / original_img_path.stem).with_suffix(".jpeg")
        if not thumb_path.exists():
            thumb_path_out = create_thumbnail(
                original_img_path, size=(512, 512), target_file=thumb_path
            )
            assert thumb_path_out == thumb_path
        annotation["thumbnail"] = thumb_path.as_posix()


def delete_non_included(annotations: List[Dict[str, Any]]):
    delete_indices = []
    for i, annotation in enumerate(annotations):
        if not annotation["included"]:
            delete_indices.append(i)
            main_pic = Path(annotation["filename"])
            thumbnail = Path(annotation["thumbnail"])

            print(f"Deleting {main_pic.name}")
            try:
                main_pic.unlink(False)
            except Exception as e:
                print("Exception when deleting main pic")
                print(e)
            try:
                thumbnail.unlink(False)
            except Exception as e:
                print("Exception when deleting thumbnail")
                print(e)

    delete_indices.reverse()
    for i in delete_indices:
        del annotations[i]


def load(path: Path) -> Dict[str, Any]:
    if not path.exists():
        print(f"json file at {path} didn't exist, creating new with empty dict")
        with path.open("w+") as f:
            json.dump({"annotations": []}, f)
    with path.open("r") as f:
        try:
            print(f"json file at {path} exists, loading")
            meta = json.load(f)
            print(f"Loaded {len(meta['annotations'])} annotations")
        except json.JSONDecodeError:
            meta = {}
            print(f"Couldn't decode {path} as json, overwriting and loading empty dict")
    return meta


def dump(meta: Dict[str, Any], path: Path):
    with path.open("w") as f:
        json.dump(meta, f, indent=4, sort_keys=True)
    print(f"Dumped {len(meta['annotations'])} annotations")


def get_suffix(s: str) -> int:
    assert "_" in s
    i = s.rfind("_")
    return int(s[i + 1 :])


def create_selection_column(annotations: List[Dict[str, Any]], selection_column: List):
    assert len(selection_column) == 0
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
                # sg.Text(annotation["layout"]),
            ]
        )
        radio_default = False


def main():
    meta = load(METADATA_PATH)

    if "annotations" not in meta:
        meta["annotations"] = []
    annotations: List[Dict[str, Any]] = meta["annotations"]

    filenames = image_files(IMG_DIR)
    populate_annotations(annotations, filenames)
    create_thumbnails(annotations, THUMB_DIR)

    dump(meta, METADATA_PATH)

    selection_column = []
    create_selection_column(annotations, selection_column)

    viewer_column = [
        [sg.Text("", key="filename")],
        [sg.Image(key="image", size=(512, 512))],
        [sg.Button("Delete non-included", key="delete_non_included")],
    ]

    layout = [
        [
            sg.Column(selection_column, scrollable=True),
            sg.VSeparator(),
            sg.Column(viewer_column),
        ],
    ]

    window = sg.Window("Image Viewer", layout, size=(1024, 1024), resizable=True)

    image_viewer: sg.Image = window["image"]
    filename_text: sg.Text = window["filename"]

    while True:
        event: str
        values: Dict[str, Any]
        event, values = window.read()
        if event is sg.WIN_CLOSED or event == "Exit":
            break
        elif event.startswith("included_"):
            assert isinstance(values[event], bool)
            i = get_suffix(event)
            annotation = annotations[i]
            annotation["included"] = values[event]
        elif event.startswith("radio_"):
            assert isinstance(values[event], bool)
            assert values[event]
            i = get_suffix(event)
            annotation = annotations[i]

            filename_text.update(
                "\n".join(
                    (
                        annotation["filename"],
                        annotation["datetime"],
                        weekday(annotation["datetime"]),
                    )
                )
            )

            thumbnail_filename = annotation["thumbnail"]
            if thumbnail_filename.lower().endswith(JPEG_SUFFIXES):
                img = to_png(thumbnail_filename)
                image_viewer.update(data=img)
            else:
                image_viewer.update(filename=thumbnail_filename, size=(512, 512))

        elif event == "delete_non_included":
            delete_non_included(annotations)
            dump(meta, METADATA_PATH)
            selection_column.clear()
            create_selection_column(annotations, selection_column)

    dump(meta, METADATA_PATH)


if __name__ == "__main__":
    main()
