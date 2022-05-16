#!/usr/bin/env python3

import io
from typing import Dict, List
import PySimpleGUI as sg
import pandas as pd
import json
import os
import helpers
from pprint import pformat, pprint

METADATA_PATH = "./metadata.json"
IMG_DIR = "./imgs"


def image_files(dir):
    filenames = [
        os.path.join(dir, f)
        for f in os.listdir(dir)
        if os.path.isfile(os.path.join(dir, f))
        and f.lower().endswith((".png", ".jpeg", ".jpg"))
    ]

    return filenames


def populate_annotations(annotations, filenames):
    for f in filenames:
        # Check if filename exists in the annotations list
        annotation = next(
            (a for a in annotations if "filename" in a and a["filename"] == f), None
        )
        # If it isn't, create an entry
        if annotation is None:
            annotation = {
                "filename": f,
            }
            annotations.append(annotation)


def get_headers(annotations: List[Dict]):
    headers = set()
    for a in annotations:
        headers.update(a.keys())
    return headers


if __name__ == "__main__":
    with open(METADATA_PATH, "r") as f:
        meta = json.load(f)

    if "annotations" not in meta:
        meta["annotations"] = []
    annotations: List[Dict] = meta["annotations"]

    filenames = image_files(IMG_DIR)

    pprint(filenames)

    populate_annotations(annotations, filenames)

    headers = get_headers(annotations)

    print(headers)

    with open(METADATA_PATH, "w") as f:
        json.dump(meta, f, indent=4, sort_keys=True)
